import pytest
from .services.agent1_extraction.extractor import Agent1Extraction
from .services.creator import run_full_ai_analysis
from ats.applications.models.applications_model import Application


@pytest.mark.django_db
def test_agent1_extraction():
    app = Application.objects.first()  
    if app and app.cv_file:
        agent = Agent1Extraction(app.cv_file.path)
        profile = agent.run()
        assert isinstance(profile, dict)
        assert "skills" in profile
        print("Agent 1 OK:", profile["skills"][:5])