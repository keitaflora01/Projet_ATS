
import os
import django
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.pdfgen import canvas
from io import BytesIO
import time

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

def create_dummy_pdf(text_content, filename="test_cv.pdf"):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "CV Test")
    y = 700
    for line in text_content.split('\n'):
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 750
    p.showPage()
    p.save()
    return ContentFile(buffer.getvalue(), name=filename)

def run_ranking_test():
    print("🚀 Démarrage du test de CLASSEMENT de l'agent IA...")

    # 1. Création Recruteur & Job
    # Use a unique email to avoid conflicts if creating multiple times
    timestamp = int(time.time())
    email = f"recruiter_rank_{timestamp}@example.com"
    user, _ = User.objects.get_or_create(email=email, defaults={'full_name': "Ranking Recruiter"})
    recruiter, _ = Recruiter.objects.get_or_create(user=user)
    
    job = JobOffer.objects.create(
        recruiter=recruiter,
        title=f"Senior DevOps Engineer {timestamp}",
        description="""
        Nous cherchons un expert DevOps / SRE.
        Compétences requises :
        - Maîtrise de Docker et Kubernetes (CKA apprécié).
        - Cloud : AWS ou GCP.
        - IaC : Terraform, Ansible.
        - CI/CD : GitLab CI, Jenkins.
        - Monitoring : Prometheus, Grafana, ELK.
        - Scripting : Python, Bash.
        """,
        location="Remote",
        contract_type="CDI",
        pass_percentage=70
    )
    print(f"✅ Job créé : {job.title} (Pass score: {job.pass_percentage}%)")

    # 2. Définition des candidats et CVs
    candidates_data = [
        {
            "name": "David DevOps",
            "email": f"david_{timestamp}@example.com",
            "cv": """
            David DevOps
            Senior Site Reliability Engineer
            
            Skills:
            - 6 years exp in Cloud Infrastructure (AWS, GCP).
            - Expert in Kubernetes (CKA, CKAD certified).
            - Infrastructure as Code: Terraform, Ansible.
            - CI/CD pipelines mastery (GitLab CI, Jenkins, ArgoCD).
            - Python automation scripting.
            
            Experience:
            - Lead DevOps at CloudCorp.
            - Migrated monolithic app to microservices on K8s.
            """
        },
        {
            "name": "Eve Sysadmin",
            "email": f"eve_{timestamp}@example.com",
            "cv": """
            Eve Sysadmin
            Linux Administrator
            
            Skills:
            - 10 years Linux Sysadmin (RHEL, Debian).
            - Bash scripting expert.
            - Network configuration (iptables, DNS, DHCP).
            - Basic Docker usage.
            - Virtualization (VMware, Proxmox).
            
            Experience:
            - Sysadmin at HistoricBank.
            - Managing on-premise servers.
            """
        },
        {
            "name": "Frank Frontend",
            "email": f"frank_{timestamp}@example.com",
            "cv": """
            Frank Frontend
            Creative UI/UX Developer
            
            Skills:
            - React, Vue.js, Angular.
            - CSS3, Sass, Tailwind.
            - Figma, Adobe XD.
            - SEO optimization.
            
            Experience:
            - Frontend Dev at WebAgency.
            - Created landing pages for e-commerce.
            """
        }
    ]

    applications = []

    # 3. Création des candidatures
    for c_data in candidates_data:
        candidate_user, _ = User.objects.get_or_create(email=c_data["email"], defaults={
            'full_name': c_data["name"],
            'role': 'candidate' 
        })

        submission = Submission.objects.create(
            job_offer=job,
            candidate=candidate_user
        )
        
        pdf_file = create_dummy_pdf(c_data["cv"], filename=f"cv_{c_data['name'].replace(' ', '_')}.pdf")
        
        application = Application.objects.create(
            submission=submission,
            cv_file=pdf_file,
            years_experience=3 # Arbitrary default
        )
        applications.append((c_data["name"], application))
        print(f"✅ Candidature créée pour {c_data['name']} (ID: {application.id})")

    # 4. Exécution de l'analyse IA (MOCKÉE via OpenAI Client)
    print("\n🤖 Lancement des analyses IA (Simulées avec Mock OpenAI)...")
    
    from unittest.mock import patch, MagicMock
    import json

    # Définition des scores simulés
    mock_results = {
        "David DevOps": {"score": 92, "recommendation": "hire", "summary": "Excellent profil DevOps, maîtrise Kubernetes et AWS."},
        "Eve Sysadmin": {"score": 45, "recommendation": "wait", "summary": "Bonnes bases Linux mais manque d'expérience Cloud/K8s."},
        "Frank Frontend": {"score": 12, "recommendation": "reject", "summary": "Profil Frontend, hors sujet pour un poste DevOps."}
    }

    # Patch de la classe OpenAI dans le service
    with patch('ats.agent.services.deepseek_service.OpenAI') as MockOpenAI:
        # Configuration du mock client
        mock_client = MockOpenAI.return_value
        
        for name, app in applications:
            print(f"   ⏳ Analyse en cours pour {name}...")
            
            # Préparation de la réponse Mock pour ce candidat
            result_data = mock_results.get(name)
            
            # La réponse attendue par le service doit être un objet avec .choices[0].message.content
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "score": result_data["score"],
                "recommendation": result_data["recommendation"],
                "summary": result_data["summary"],
                "confidence": 0.95,
                "extracted_skills": ["Docker", "Linux"] if "David" in name else [],
                "matching_skills": ["Docker", "Kubernetes"] if "David" in name else [],
                "missing_skills": []
            })
            
            # On configure le mock pour retourner cette réponse à chaque appel
            mock_client.chat.completions.create.return_value = mock_response

            try:
                # Exécution synchrone (la tâche utilisera le mock)
                process_application_ai(app.id)
                print(f"      ✅ Analyse terminée pour {name} (Score simulé: {result_data['score']})")
            except Exception as e:
                print(f"      ❌ Erreur pour {name}: {e}")

    # 5. Récupération et Affichage du Classement

    # 5. Récupération et Affichage du Classement
    print("\n🏆 CLASSEMENT FINAL DES CANDIDATURES")
    print("-" * 80)
    print(f"{'Rang':<5} | {'Candidat':<20} | {'Score':<10} | {'Statut':<15} | {'Résumé IA'}")
    print("-" * 80)

    # Récupérer les applications liées à ce job, triées par score décroissant
    ranked_apps = Application.objects.filter(
        submission__job_offer=job
    ).order_by('-ia_score')

    for i, app in enumerate(ranked_apps, 1):
        candidate_name = app.submission.candidate.full_name
        score = app.ia_score or 0
        status = app.status
        summary = app.resume[:50].replace('\n', ' ') + "..." if app.resume else "Pas de résumé"

        print(f"{i:<5} | {candidate_name:<20} | {score:<10} | {status:<15} | {summary}")

    print("-" * 80)

    # Vérification simple de l'ordre
    scores = [app.ia_score or 0 for app in ranked_apps]
    if scores == sorted(scores, reverse=True):
        print("\n✅ TEST RÉUSSI : Les candidats sont bien triés par score décroissant.")
    else:
        print("\n❌ TEST ÉCHOUÉ : L'ordre de tri est incorrect.")

if __name__ == "__main__":
    run_ranking_test()
