import os
import django
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.pdfgen import canvas
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ats.users.models.user_model import User
from ats.recruiters.models.recruiters_model import Recruiter
from ats.jobs.models.jobs_model import JobOffer
from ats.submissions.models.submissions_models import Submission
from ats.applications.models.applications_model import Application
from ats.agent.tasks import process_application_ai
from ats.agent.models.analysis_result import AIAnalysisResult

def create_dummy_pdf(text_content):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "CV Test")
    y = 700
    for line in text_content.split('\n'):
        p.drawString(50, y, line)
        y -= 20
    p.showPage()
    p.save()
    return ContentFile(buffer.getvalue(), name="test_cv.pdf")

def run_test():
    print("🚀 Démarrage du test de l'agent IA...")

    # 1. Création Recruteur & Job
    email = f"recruiter_test_{timezone.now().timestamp()}@example.com"
    user, _ = User.objects.get_or_create(email=email, defaults={'full_name': "Test Recruiter"})
    recruiter, _ = Recruiter.objects.get_or_create(user=user)
    
    job = JobOffer.objects.create(
        recruiter=recruiter,
        title="Senior Python Developer",
        description="""
        Nous cherchons un expert Python / Django.
        Compétences requises :
        - Python 3.10+
        - Django & DRF
        - Celery & Redis
        - PostgreSQL
        - Docker
        - Bonnes pratiques de code (Clean Code, TDD)
        """,
        location="Paris",
        contract_type="CDI"
    )
    print(f"✅ Job créé : {job.title}")

    # 2. Création Submission & Application avec CV PDF
    candidate_email = "jean.dupont@example.com"
    candidate, _ = User.objects.get_or_create(email=candidate_email, defaults={
        'full_name': "Jean Dupont",
        'role': 'candidate' 
    })

    submission = Submission.objects.create(
        job_offer=job,
        candidate=candidate
    )
    
    cv_content = """
    Jean Dupont
    Développeur Backend Senior
    
    Expérience :
    - 5 ans de développement Python chez TechCorp.
    - Conception d'API REST avec Django Rest Framework.
    - Utilisation intensive de Celery pour les tâches asynchrones.
    - Orchestration avec Docker et Kubernetes.
    - Base de données : PostgreSQL, Redis.
    
    Formation :
    - Master Informatique
    """
    
    pdf_file = create_dummy_pdf(cv_content)
    
    application = Application.objects.create(
        submission=submission,
        cv_file=pdf_file,
        years_experience=5
    )
    print(f"✅ Candidature créée : ID {application.id}")

    # 3. Exécution de l'analyse (Synchrone)
    print("🤖 Lancement de l'analyse IA (simulation synchrone)...")
    try:
        # On appelle directement la fonction sans .delay() pour tester tout de suite
        # Mais process_application_ai est décoré @shared_task, donc on l'appelle comme une fonction normale
        process_application_ai(application.id)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de la tâche : {e}")
        return

    # 4. Vérification des résultats
    try:
        result = AIAnalysisResult.objects.get(submission_id=submission.id)
        print("\n🎉 RÉSULTATS DE L'ANALYSE (AIAnalysisResult) :")
        print(f"⭐ Score : {result.matching_score}/100")
        print(f"💡 Recommandation : {result.recommendation}")
        print(f"🔍 Compétences correspondantes : {result.matching_details.get('matching_skills')}")
        print(f"📉 Compétences manquantes : {result.matching_details.get('missing_skills')}")
        print(f"📝 Résumé : {result.recommendation_reason}")

        # Vérification sur Application (pour l'admin)
        application.refresh_from_db()
        print("\n🖥️ VÉRIFICATION AFFICHAGE ADMIN (Application Model) :")
        print(f"⭐ Application.ia_score : {application.ia_score}")
        print(f"📝 Application.resume : {application.resume[:100]}...")
        
        if application.ia_score == result.matching_score:
             print("✅ SYNC OK : Le score est bien reporté sur le modèle Application.")
        else:
             print("❌ SYNC FAIL : Le score Application est différent du résultat IA.")

    except AIAnalysisResult.DoesNotExist:
        print("❌ Aucun résultat d'analyse trouvé. L'agent a échoué silencieusement ?")

if __name__ == "__main__":
    run_test()
