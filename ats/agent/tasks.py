# ats/agent/tasks.py
from celery import shared_task
from django.utils import timezone
import time
import traceback
import json

from ats.applications.models.applications_model import Application
from ats.agent.models.analysis_result import AIAnalysisResult
from ats.agent.services.gemini_service import analyze_with_gemini  # ton service Gemini


@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # 3 retries, 1 min d'attente
def process_application_ai(self, application_id):
    """
    Tâche Celery qui lance l'analyse complète avec Gemini pour une candidature.
    - Extrait texte CV/LM
    - Appelle Gemini
    - Stocke le résultat dans AIAnalysisResult
    """
    start_time = time.time()
    app = None

    try:
        # Récupération optimisée de l'application
        app = Application.objects.select_related(
            'submission', 'submission__job_offer'
        ).get(id=application_id)

        print(f"[CELERY START] Analyse Gemini pour application {application_id} "
              f"(candidature {app.submission_id}) - {timezone.now()}")

        # Extraction du texte (si pas déjà fait)
        cv_text = ""
        if app.cv_file:
            try:
                cv_text = app.cv_file.read().decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"[CV READ ERROR] {e}")

        cover_text = ""
        if app.cover_letter_file:
            try:
                cover_text = app.cover_letter_file.read().decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"[LM READ ERROR] {e}")

        job_description = app.submission.job_offer.description or ""

        # Appel à Gemini (ton service)
        analysis_result = analyze_with_gemini(
            cv_text=cv_text,
            cover_text=cover_text,
            job_description=job_description
        )

        duration = time.time() - start_time

        # Sauvegarde ou mise à jour du résultat
        analysis, created = AIAnalysisResult.objects.update_or_create(
            submission=app.submission,
            defaults={
                "score": analysis_result.get("score", 0),
                "extracted_skills": analysis_result.get("extracted_skills", []),
                "matching_skills": analysis_result.get("matching_skills", []),
                "missing_skills": analysis_result.get("missing_skills", []),
                "summary": analysis_result.get("summary", ""),
                "raw_response": json.dumps(analysis_result),
                "processed_at": timezone.now(),
                "processing_duration": duration,
                "ai_model_version": "gemini-1.5-flash (free tier)",
                "confidence": analysis_result.get("confidence", 0.5),
            }
        )

        print(f"[CELERY SUCCESS] Analyse terminée - Score: {analysis.score} | "
              f"Durée: {duration:.2f}s | Créé: {created}")

    except Application.DoesNotExist:
        print(f"[CELERY ERROR] Application {application_id} introuvable")
        return  # Pas de retry, objet inexistant

    except Exception as exc:
        error_msg = f"[CELERY CRITICAL ERROR] {str(exc)}\n{traceback.format_exc()}"
        print(error_msg)

        # Gestion intelligente des erreurs
        if "429" in str(exc) or "quota" in str(exc).lower() or "rate limit" in str(exc).lower():
            print("[CELERY QUOTA] Limite Gemini gratuite atteinte → retry dans 1h")
            raise self.retry(exc=exc, countdown=3600)  # 1 heure

        # Autres erreurs → retry normal (3 fois max)
        raise self.retry(exc=exc, countdown=60)

    finally:
        if app:
            # Optionnel : mise à jour d'un champ "analyzed_at" sur Application
            app.analyzed_at = timezone.now()
            app.save(update_fields=['analyzed_at'])
            