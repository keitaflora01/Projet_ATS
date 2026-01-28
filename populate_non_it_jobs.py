import os
import django
import random
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ats.users.models import User
from ats.recruiters.models import RecruiterProfile
from ats.jobs.models.jobs_model import JobOffer, JobType, ContractType

def populate_non_it():
    print("--- Populating Non-IT Jobs ---")
    
    # Ensure Recruiter exists
    user, _ = User.objects.get_or_create(email="recruiter_general@example.com", defaults={"role": "recruiter"})
    recruiter, _ = RecruiterProfile.objects.get_or_create(user=user, defaults={"company_name": "General Industries"})
    
    jobs_data = [
        ("Chef de Cuisine", "Experience with French cuisine, ability to manage a team of 10. HACCP knowledge required."),
        ("Medical Nurse", "State Registered Nurse (IDE) for night shifts. ICU experience preferred. Patience and rigor."),
        ("Sales Manager", "B2B sales experience in the automotive sector. Negotiation skills, English required."),
        ("Truck Driver", "Heavy vehicle license (Permis CE + FIMO). National transport. Punctuality and safety."),
        ("Baker / Pâtissier", "Artisan baker needed for morning shifts. Sourdough bread and pastries mastery."),
        ("Accountant", "General accounting, payroll, and tax declarations. Sage/Excel proficiency."),
        ("Civil Engineer", "Construction site supervision, autocad skills, structural analysis."),
        ("HR Business Partner", "Recruitment, employee relations, labor law knowledge."),
        ("Marketing Coordinator", "Event planning, social media management (non-technical), brand awareness."),
        ("Receptionist", "Welcoming guests, managing calls, multilingual (French/English/Spanish).")
    ]
    
    for title, desc in jobs_data:
        job, created = JobOffer.objects.get_or_create(
            title=title,
            recruiter=recruiter,
            defaults={
                "description": desc,
                "job_type": random.choice(JobType.values),
                "contract_type": random.choice(ContractType.values),
                "location": random.choice(["Paris", "Lyon", "Marseille", "Bordeaux"]),
                "is_remote": False,
                "salary_min": random.randint(25, 45) * 1000,
                "salary_max": random.randint(46, 70) * 1000,
                "pass_percentage": 70,
                "published_at": timezone.now() - timedelta(days=random.randint(0, 30))
            }
        )
        if created:
            print(f"✅ Created: {title}")
        else:
            print(f"ℹ️ Exists: {title}")
            
    print("--- Done ---")

if __name__ == "__main__":
    populate_non_it()
