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

def populate():
    print("--- Populating Jobs ---")
    
    # Ensure Recruiter exists
    user, _ = User.objects.get_or_create(email="recruiter_demo@example.com", defaults={"role": "recruiter"})
    recruiter, _ = RecruiterProfile.objects.get_or_create(user=user, defaults={"company_name": "Demo Corp"})
    
    titles = [
        "Backend Developer Python",
        "Frontend Developer React",
        "Fullstack Engineer",
        "Data Scientist",
        "DevOps Engineer",
        "Product Manager",
        "UI/UX Designer",
        "QA Engineer",
        "Mobile Developer (Flutter)",
        "CTO"
    ]
    
    descriptions = [
        "We are looking for a passionate developer to join our team.",
        "Join a fast-growing startup working on AI.",
        "Great opportunity for career growth.",
         "Remote friendly position with competitive salary."
    ]
    
    for i, title in enumerate(titles):
        job, created = JobOffer.objects.get_or_create(
            title=title,
            recruiter=recruiter,
            defaults={
                "description": f"{random.choice(descriptions)} Required skills: Python, Django, React. {title} role.",
                "job_type": random.choice(JobType.values),
                "contract_type": random.choice(ContractType.values),
                "location": random.choice(["Paris", "Lyon", "Remote", "New York", "London"]),
                "is_remote": random.choice([True, False]),
                "salary_min": random.randint(30, 60) * 1000,
                "salary_max": random.randint(65, 100) * 1000,
                "pass_percentage": 70, # Default pass percentage
                "published_at": timezone.now() - timedelta(days=random.randint(0, 30))
            }
        )
        if created:
            print(f"✅ Created: {title}")
        else:
            print(f"ℹ️ Exists: {title}")
            
    print("--- Done ---")

if __name__ == "__main__":
    populate()
