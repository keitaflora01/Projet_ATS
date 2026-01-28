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
                    text = ""
                    import io
                    
                    # Read content to memory to ensure we have a standard BytesIO object
                    # This avoids issues with Django's FieldFile/File wrappers
                    try:
                        file_obj.seek(0)
                        content = file_obj.read()
                        stream = io.BytesIO(content)
                    except Exception as e:
                        print(f"⚠️ Erreur lecture fichier PDF vers mémoire: {e}")
                        return ""

                    try:
                        # Strategy 1: pdfminer.six (More robust)
                        from pdfminer.high_level import extract_text as pdfminer_extract
                        text = pdfminer_extract(stream)
                    except ImportError:
                        print("⚠️ pdfminer.six not installed, trying pypdf...")
                        pass
                    except Exception as e:
                        print(f"⚠️ pdfminer error: {e}")

                    if not text.strip():
                        # Strategy 2: pypdf (Fallback)
                        try:
                            import pypdf
                            stream.seek(0) # Reset cursor
                            reader = pypdf.PdfReader(stream)
                            for i, page in enumerate(reader.pages):
                                try:
                                    page_text = page.extract_text()
                                    if page_text:
                                        text += page_text + "\n"
                                except Exception as e:
                                    print(f"⚠️ Erreur extraction page PDF {i} (pypdf): {e}")
                        except Exception as e:
                             print(f"⚠️ pypdf error: {e}")
                    
                    if not text.strip():
                         print("⚠️ Aucun texte extrait du PDF après multiples tentatives.")
                    
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
        print(f"[DEBUG] Extracted CV Text Length: {len(cv_text)}")
        print(f"[DEBUG] CV Text Preview: {cv_text[:200]}")
        
        if not cv_text:
             print("⚠️ CV vide ou illisible après extraction.")
        
        # Extraction LM
        lm_text = extract_text_from_file(app.cover_letter_file)

        job_desc = app.submission.job_offer.description or ""
        print(f"[DEBUG] Job Offer: {app.submission.job_offer.title}")

        # CALL DEEPSEEK SERVICE
        analysis = analyze_with_deepseek(cv_text, lm_text, job_desc)
        
        print(f"[DEBUG] AI Raw Response: {analysis}")

        duration = time.time() - start_time
        
        score = analysis.get("score", 0)
        
        # update Analysis Result
        AIAnalysisResult.objects.update_or_create(
            submission=app.submission,
            defaults={
                "matching_score": score,
                "extracted_profile": {
                    "skills": analysis.get("extracted_skills", [])
                },
                "matching_details": {
                    "matching_skills": analysis.get("matching_skills", []),
                    "missing_skills": analysis.get("missing_skills", []),
                    "full_summary": analysis.get("summary", "")
                },
                "recommendation": analysis.get("recommendation", "wait"),
                "recommendation_reason": analysis.get("summary", "")[:500],
                "confidence": analysis.get("confidence", 0.5),
                "processed_at": timezone.now(),
                "processing_duration": timedelta(seconds=duration),
                "ai_model_version": "deepseek-v3",
            }
        )
        
        # Update Application Score
        app.ia_score = score
        app.resume = analysis.get("summary", "")[:5000]
        
        # CHECK PASS PERCENTAGE
        job_offer = app.submission.job_offer
        pass_percentage = job_offer.pass_percentage
        
        print(f"[CELERY] Score: {score} / Pass: {pass_percentage}")

        if score >= pass_percentage:
            from ats.applications.models.applications_model import ApplicationStatus
            from ats.interviews.models.interview_model import Interview, InterviewStatus
            from ats.agent.services.deepseek_service import generate_interview_questions
            from ats.utility.email_service import send_interview_invitation
            
            # 1. Update Status
            app.status = ApplicationStatus.INTERVIEW
            app.save()
            print(f"[CELERY] Candidat PASSED. Status -> INTERVIEW")
            
            # 2. Generate Interview Questions
            questions = generate_interview_questions(job_desc, cv_text)
            
            # 3. Create Interview Object
            Interview.objects.create(
                application=app,
                job_offer=job_offer,
                questions=questions,
                status=InterviewStatus.SCHEDULED
            )
            print(f"[CELERY] Interview created with {len(questions)} questions.")
            
            # 4. Send Email
            send_interview_invitation(app)
            
        else:
            # Optionally update status to REJECTED or leave as PENDING/REVIEW
            # For now we leave logic to recruiter or set to REVIEW
            pass
            
            app.save()

        print(f"[CELERY SUCCESS] Score: {score} | Durée: {duration:.2f}s")

    except Exception as e:
        print(f"[CELERY ERROR] {str(e)}\n{traceback.format_exc()}")
        raise self.retry(exc=e, countdown=60)