from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ats.users.models.user_model import User, UserRole
from ats.candidates.models.candidates_model import Candidate
from ats.recruiters.models.recuiters_model import Recruiter

class AuthTests(APITestCase):

    def test_register_candidate(self):
        url = reverse('register')
        data = {
            "email": "candidate@test.com",
            "password": "Password123!",
            "password2": "Password123!",
            "role": "candidate"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(Candidate.objects.first().user.email, "candidate@test.com")

    def test_register_recruiter_success(self):
        url = reverse('register')
        data = {
            "email": "recruiter@test.com",
            "password": "Password123!",
            "password2": "Password123!",
            "role": "recruiter",
            "company_name": "Test Company"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Recruiter.objects.count(), 1)
        self.assertEqual(Recruiter.objects.first().user.email, "recruiter@test.com")
        self.assertEqual(Recruiter.objects.first().company_name, "Test Company")

    def test_register_recruiter_missing_company(self):
        url = reverse('register')
        data = {
            "email": "recruiter2@test.com",
            "password": "Password123!",
            "password2": "Password123!",
            "role": "recruiter"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company_name", response.data)

    def test_login_response_has_role(self):
        user = User.objects.create_user(email="user@test.com", password="Password123!", role="candidate")
        user.is_active = True
        user.save()
        
        url = reverse('login')
        data = {
            "email": "user@test.com",
            "password": "Password123!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("role", response.data)
        self.assertEqual(response.data["role"], "candidate")
        self.assertIn("access", response.data)
