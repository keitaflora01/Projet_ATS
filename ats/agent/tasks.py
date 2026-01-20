from celery import shared_task
from django.utils import timezone
import time
import traceback

from ats.applications.models.applications_model import Application
from ats.agent.models.analysis_result import AIAnalysisResult
from ats.agent.services.gemini_service import analyze_with_gemini


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_application_ai(self, application_id):
    start_time = time.time()
    try:
        app = Application.objects.select_related('submission', 'submission__job_offer').get(id=application_id)
        print(f"[CELERY START] Analyse pour ID {application_id}")

        cv_text = app.cv_file.read().decode('utf-8', errors='ignore') if app.cv_file else ""
        lm_text = app.cover_letter_file.read().decode('utf-8', errors='ignore') if app.cover_letter_file else ""
        job_desc = app.submission.job_offer.description or ""

        analysis = analyze_with_gemini(cv_text, lm_text, job_desc)

        duration = time.time() - start_time

        AIAnalysisResult.objects.update_or_create(
            submission=app.submission,
            defaults={
                "score": analysis.get("score", 0),
                "extracted_skills": analysis.get("extracted_skills", []),
                "matching_skills": analysis.get("matching_skills", []),
                "missing_skills": analysis.get("missing_skills", []),
                "summary": analysis.get("summary", ""),
                "recommendation": analysis.get("recommendation", "wait"),
                "confidence": analysis.get("confidence", 0.5),
                "processed_at": timezone.now(),
                "processing_duration": duration,
                "ai_model_version": "gemini-1.5-flash",
            }
        )

        print(f"[CELERY SUCCESS] Score: {analysis.get('score')} | Durée: {duration:.2f}s")

    except Exception as e:
        print(f"[CELERY ERROR] {str(e)}\n{traceback.format_exc()}")
        raise self.retry(exc=e, countdown=60)