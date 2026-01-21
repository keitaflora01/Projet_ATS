
import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from ats.recruiters.models.recruiters_model import RecruiterProfile
from ats.jobs.models.jobs_model import JobOffer

User = get_user_model()

def populate():
    print("--- Pupulating Jobs ---")
    
    # Ensure we have a recruiter
    email = "recruiter_demo@example.com"
    user, created = User.objects.get_or_create(email=email, defaults={
        "role": "recruiter", 
        "is_active": True
    })
    if created:
        user.set_password("password123")
        user.save()
        print(f"Created recruiter user: {email}")
    
    recruiter, r_created = RecruiterProfile.objects.get_or_create(user=user, defaults={
        "company_name": "Tech Corp Inc."
    })
    
    jobs_data = [
        {"title": "Senior Python Developer", "location": "Paris, Remote"},
        {"title": "Frontend React Engineer", "location": "Lyon, Hybrid"},
        {"title": "AI Research Scientist", "location": "Sophia Antipolis"},
        {"title": "DevOps Specialist", "location": "Bordeaux"},
        {"title": "Product Manager", "location": "Remote"},
    ]
    
    for job in jobs_data:
        JobOffer.objects.create(
            recruiter=recruiter,
            title=job["title"],
            description=f"We are looking for a {job['title']} to join our amazing team. Minimum 3 years experience required. Competitive salary.",
            location=job["location"],
            salary_min=40000,
            salary_max=80000,
            job_type="full_time",
            contract_type="cdi"
        )
        print(f"Created job: {job['title']}")

if __name__ == "__main__":
    populate()
