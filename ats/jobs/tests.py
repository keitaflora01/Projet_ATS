# ats/jobs/tests.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ats.users.models.user_model import User
from ats.recruiters.models import RecruiterProfile
from ats.jobs.models.jobs_model import JobOffer

class JobOfferAPITest(APITestCase):
    def setUp(self):
        # Créer un recruteur
        self.recruiter_user = User.objects.create_user(
            email="recruteur@test.com",
            full_name="Recruteur Test",
            role="recruiter",
            password="pass123456"
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user,
            company_name="Test Corp",
            company_website="https://testcorp.com"
        )

        # Créer un candidat pour tests futurs
        self.candidate_user = User.objects.create_user(
            email="candidat@test.com",
            role="candidate",
            password="pass123456"
        )

        self.client = APIClient()

    def test_recruiter_can_create_job(self):
        self.client.force_authenticate(user=self.recruiter_user)
        
        data = {
            "title": "Développeur Python Senior",
            "description": "Nous recherchons un expert...",
            "job_type": "full_time",
            "location": "Paris",
            "is_remote": True,
            "salary_min": 50000.00,
            "salary_max": 70000.00,
            "is_active": True
        }
        
        response = self.client.post("/jobs/api/offers/", data, format="json")
        print("Status code:", response.status_code)
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobOffer.objects.count(), 1)
        self.assertEqual(JobOffer.objects.first().title, "Développeur Python Senior")
        self.assertEqual(JobOffer.objects.first().recruiter, self.recruiter_profile)

    def test_candidate_cannot_create_job(self):
        self.client.force_authenticate(user=self.candidate_user)
        data = {"title": "Test", "description": "Test"}
        response = self.client.post("/jobs/api/offers/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)