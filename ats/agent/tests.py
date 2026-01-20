# ats/agent/tests.py
import pytest
from django.test import TestCase
from ats.agent.cv_Agent import CVAgent
from ats.agent.LM_Agent import LMAgent
from ats.agent.tasks import process_application_ai
from ats.applications.models.applications_model import Application  # Importe pour mock

@pytest.mark.django_db
class AgentTests(TestCase):
    def test_cv_agent(self):
        agent = CVAgent('/path/to/test_cv.pdf')  # Remplace par un vrai chemin
        profile = agent.analyze()
        assert isinstance(profile, dict)
        assert "skills" in profile

    def test_lm_agent(self):
        agent = LMAgent('/path/to/test_lm.pdf')
        insights = agent.analyze()
        assert isinstance(insights, dict)
        assert "motivation_level" in insights

    def test_process_task(self):
        # Mock une application (crée-en une vraie pour test)
        app = Application.objects.first()
        if app:
            result = process_application_ai.delay(app.id)
            assert result.status == "SUCCESS"  
            