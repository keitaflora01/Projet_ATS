# ats/agent/tests/test_flow_logic.py
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from ats.users.models import User
from ats.recruiters.models import RecruiterProfile
from ats.jobs.models.jobs_model import JobOffer
from ats.submissions.models.submissions_models import Submission
from ats.applications.models.applications_model import Application, ApplicationStatus
from ats.interviews.models.interview_model import Interview
from ats.agent.tasks import process_application_ai

@pytest.mark.django_db
class TestATSFlow:
    def setup_method(self):
        # Create Users
        self.recruiter_user = User.objects.create_user(email="recruiter@example.com", password="password", role="recruiter")
        self.candidate_user = User.objects.create_user(email="candidate@example.com", password="password", role="candidate", first_name="John", last_name="Doe")
        
        # Create Profile
        self.recruiter_profile = RecruiterProfile.objects.create(user=self.recruiter_user, company_name="Test Corp")
        
        # Create Job with pass percentage 70
        self.job = JobOffer.objects.create(
            recruiter=self.recruiter_profile,
            title="Python Dev",
            description="We need a Python Dev.",
            pass_percentage=70
        )
        
        # Create Submission & Application
        self.submission = Submission.objects.create(candidate=self.candidate_user, job_offer=self.job)
        self.application = Application.objects.create(submission=self.submission)

    @patch("ats.agent.tasks.analyze_with_deepseek")
    @patch("ats.agent.tasks.generate_interview_questions")
    @patch("ats.agent.tasks.send_interview_invitation")
    def test_flow_success_high_score(self, mock_send_email, mock_gen_questions, mock_analyze):
        """Test flow when candidate score is ABOVE pass percentage (80 > 70)"""
        
        # Mock DeepSeek Analysis Response
        mock_analyze.return_value = {
            "score": 80,
            "recommendation": "interview",
            "summary": "Good candidate",
            "confidence": 0.9,
            "extracted_skills": ["python"],
            "matching_skills": ["python"],
            "missing_skills": []
        }
        
        # Mock Question Generation
        mock_gen_questions.return_value = ["Q1?", "Q2?"]
        
        # Run Task
        process_application_ai(self.application.id)
        
        # Refresh from DB
        self.application.refresh_from_db()
        
        # ASSERTIONS
        assert self.application.ia_score == 80
        assert self.application.status == ApplicationStatus.INTERVIEW
        
        # Check Interview Created
        assert Interview.objects.filter(application=self.application).exists()
        interview = Interview.objects.get(application=self.application)
        assert interview.questions == ["Q1?", "Q2?"]
        
        # Check Email Sent
        mock_send_email.assert_called_once()

    @patch("ats.agent.tasks.analyze_with_deepseek")
    @patch("ats.agent.tasks.generate_interview_questions")
    @patch("ats.agent.tasks.send_interview_invitation")
    def test_flow_fail_low_score(self, mock_send_email, mock_gen_questions, mock_analyze):
        """Test flow when candidate score is BELOW pass percentage (50 < 70)"""
        
        # Mock DeepSeek Analysis Response
        mock_analyze.return_value = {
            "score": 50,
            "recommendation": "reject",
            "summary": "Not enough skills",
            "confidence": 0.9,
            "extracted_skills": [],
            "matching_skills": [],
            "missing_skills": ["python"]
        }
        
        # Run Task
        process_application_ai(self.application.id)
        
        # Refresh from DB
        self.application.refresh_from_db()
        
        # ASSERTIONS
        assert self.application.ia_score == 50
        assert self.application.status != ApplicationStatus.INTERVIEW  # Should NOT be interview
        
        # Check NO Interview Created
        assert not Interview.objects.filter(application=self.application).exists()
        
        # Check NO Email Sent
        mock_send_email.assert_not_called()
