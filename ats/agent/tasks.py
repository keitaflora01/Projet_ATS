from celery import shared_task
from django.utils import timezone
import time
import time
import traceback
from datetime import timedelta

from ats.applications.models.applications_model import Application
from ats.agent.models.analysis_result import AIAnalysisResult
from ats.agent.services.deepseek_service import analyze_with_deepseek  # Switch to DeepSeek

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_application_ai(self, application_id):
    start_time = time.time()
    try:
        app = Application.objects.select_related('submission', 'submission__job_offer').get(id=application_id)
        print(f"[CELERY START] Analyse (DeepSeek) pour ID {application_id}")


        def extract_text_from_file(file_obj):
            if not file_obj:
                return ""
            
            try:
                name = file_obj.name.lower()
                limit_size = 5 * 1024 * 1024  # 5 MB safety limit for reading to memory
                
                if file_obj.size > limit_size:
                    print(f"⚠️ Fichier trop volumineux ({file_obj.size} bytes), lecture partielle.")
                    # Fallback logic could go here, but for now we proceed cautiously
                
                if name.endswith('.pdf'):
                    import pypdf
                    reader = pypdf.PdfReader(file_obj)
                    text = ""
                    for page in reader.pages:
                        try:
                            text += (page.extract_text() or "") + "\n"
                        except Exception as e:
                            print(f"⚠️ Erreur extraction page PDF: {e}")
                    return text
                
                elif name.endswith('.docx'):
                    import docx
                    doc = docx.Document(file_obj)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    return text
                
                else:
                    # Fallback for txt or other raw formats
                    file_obj.seek(0)
                    return file_obj.read().decode('utf-8', errors='ignore')
            
            except Exception as e:
                print(f"❌ Erreur extraction texte ({file_obj.name}): {str(e)}")
                return ""

        # Extraction CV
        cv_text = extract_text_from_file(app.cv_file)
        if not cv_text:
             print("⚠️ CV vide ou illisible après extraction.")
        
        # Extraction LM
        lm_text = extract_text_from_file(app.cover_letter_file)

        job_desc = app.submission.job_offer.description or ""

        # CALL DEEPSEEK SERVICE
        analysis = analyze_with_deepseek(cv_text, lm_text, job_desc)

        duration = time.time() - start_time

        AIAnalysisResult.objects.update_or_create(
            submission=app.submission,
            defaults={
                "matching_score": analysis.get("score", 0),
                "extracted_profile": {
                    "skills": analysis.get("extracted_skills", [])
                },
                "matching_details": {
                    "matching_skills": analysis.get("matching_skills", []),
                    "missing_skills": analysis.get("missing_skills", []),
                    "full_summary": analysis.get("summary", "")
                },
                "recommendation": analysis.get("recommendation", "wait"),
                "recommendation_reason": analysis.get("summary", "")[:500],  # Truncate if needed
                "confidence": analysis.get("confidence", 0.5),
                "processed_at": timezone.now(),
                "processing_duration": timedelta(seconds=duration), # Fix type
                "ai_model_version": "deepseek-v3",
            }
        )

        print(f"[CELERY SUCCESS] Score: {analysis.get('score')} | Durée: {duration:.2f}s")

    except Exception as e:
        print(f"[CELERY ERROR] {str(e)}\n{traceback.format_exc()}")
        raise self.retry(exc=e, countdown=60)