
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ats.jobs.models.jobs_model import JobOffer
from ats.recruiters.models.recruiters_model import Recruiter

def find_job():
    print("🔍 Recherche de l'offre DevOps chez Hooyia...")
    
    # Try to find by company name or title
    jobs = JobOffer.objects.filter(
        title__icontains="devops"
    )
    
    found = False
    for job in jobs:
        print(f"✅ Trouvé : ID={job.id} | Titre={job.title} | Recruteur={job.recruiter.user.full_name} | Entreprise={job.recruiter.company_name}")
        if "hooyia" in job.recruiter.company_name.lower():
            found = True
            print("   🎯 C'est l'offre cible !")
            
    if not found:
        print("⚠️ Aucune offre 'DevOps' trouvée pour l'entreprise 'Hooyia'.")
        # List all recruiters to help debug
        print("\nRecruteurs disponibles :")
        for r in Recruiter.objects.all():
            print(f"- {r.user.full_name} ({r.company_name})")

if __name__ == "__main__":
    find_job()
