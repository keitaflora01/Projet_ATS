# ats/agent/tasks.py
from celery import shared_task
from django.utils import timezone
import time
import traceback
from datetime import timedelta
from django.db import IntegrityError

from ats.applications.models.applications_model import Application
from ats.agent.models.analysis_result import AIAnalysisResult
from ats.agent.services.deepseek_service import analyze_with_deepseek


def extract_text_from_file(file_obj):
    """Extraction texte sécurisée"""
    if not file_obj:
        return ""

    try:
        file_obj.seek(0)  # ← IMPORTANT !
        name = file_obj.name.lower()

        if name.endswith('.pdf'):
            import pypdf
            reader = pypdf.PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text

        elif name.endswith('.docx'):
            import docx
            doc = docx.Document(file_obj)
            return "\n".join([para.text for para in doc.paragraphs])

        else:
            return file_obj.read().decode('utf-8', errors='ignore')

    except Exception as e:
        print(f"❌ Erreur extraction ({file_obj.name}): {str(e)}")
        return ""


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_application_ai(self, application_id):
    start_time = time.time()
    try:
        app = Application.objects.select_related(
            'submission', 'submission__job_offer'
        ).get(id=application_id)

        print(f"[CELERY START] Analyse DeepSeek pour application {application_id} - {timezone.now()}")

        cv_text = extract_text_from_file(app.cv_file)
        lm_text = extract_text_from_file(app.cover_letter_file) if app.cover_letter_file else ""
        job_desc = app.submission.job_offer.description or ""

        analysis = analyze_with_deepseek(cv_text, lm_text, job_desc)

        # GUARD: Verify submission existence via ID
        if not app.submission_id:
            print(f"[CELERY ERROR] Application {application_id} has no linked submission ID. Aborting analysis.")
            return

        duration = time.time() - start_time

        defaults={
            "matching_score": analysis.get("score", 0),
            "extracted_profile": {"skills": analysis.get("extracted_skills", [])},
            "matching_details": {
                "matching_skills": analysis.get("matching_skills", []),
                "missing_skills": analysis.get("missing_skills", []),
                "full_summary": analysis.get("summary", "")
            },
            "recommendation": analysis.get("recommendation", "wait"),
            "recommendation_reason": analysis.get("summary", "")[:500],
            "confidence": analysis.get("confidence", 0.5),
            "processed_at": timezone.now(),
            "processing_duration": timedelta(seconds=int(duration)),
            "ai_model_version": "deepseek-v3",
            "raw_ai_response": analysis,
        }

        print(f"[DEBUG] Submission ID: {app.submission_id}")

        try:
            analysis_result = AIAnalysisResult.objects.get(submission_id=app.submission_id)
            print("[DEBUG] Updating existing AnalysisResult")
            for key, value in defaults.items():
                setattr(analysis_result, key, value)
            analysis_result.save()
            created = False
        except AIAnalysisResult.DoesNotExist:
            print("[DEBUG] Creating new AnalysisResult")
            analysis_result = AIAnalysisResult(submission_id=app.submission_id, **defaults)
            analysis_result.save()
            created = True

        # Sync back to Application model for Admin display
        app.ia_score = analysis_result.matching_score
        app.resume = analysis_result.recommendation_reason[:500]  # Respect max_length if any, or just truncated
        # Map recommendation to status if needed, or just keep it separate
        app.save(update_fields=['ia_score', 'resume'])


        print(f"[CELERY SUCCESS] Analyse terminée - Score: {analysis_result.matching_score} | "
              f"Durée: {duration:.2f}s | Créé: {created}")

    except Application.DoesNotExist:
        print(f"[CELERY ERROR] Application {application_id} introuvable")
    
    except IntegrityError as exc:
        print(f"[CELERY FATAL] Erreur d'intégrité (base de données) : {exc}")
        # Ne pas réessayer sur une erreur de base de données (probablement fatale)
        return

    except Exception as exc:
        error_msg = f"[CELERY ERROR] {str(exc)}\n{traceback.format_exc()}"
        print(error_msg)

        # Check for specific API rate limit / quota errors
        # Make sure we don't catch our own error payloads from the DB
        # Only retry if it looks like a real network/api exception
        str_exc = str(exc).lower()
        if any(x in str_exc for x in ["quota", "rate limit", "429", "too many requests"]):
            print("[CELERY QUOTA] Problème DeepSeek → retry dans 1h")
            raise self.retry(exc=exc, countdown=3600)
        
        # If it's just 'api key missing' in a returned string, it shouldn't be an exception here unless we raised it.
        # But if the exception itself is about API key (e.g. AuthenticationError from library)
        if "api key" in str_exc or "clé api" in str_exc:
             # Verify it's not the IntegrityError text causing this (handled above by IntegrityError block)
             print("[CELERY API KEY] Problème Clé API → retry dans 1h")
             raise self.retry(exc=exc, countdown=3600)

        raise self.retry(exc=exc, countdown=60)