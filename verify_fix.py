import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append("/home/keita/ats")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# We don't need full django setup for unit test with mocks, but imports might need it
import django
django.setup()

from ats.agent.tasks import process_application_ai
from ats.applications.models.applications_model import Application

class TestProcessApplicationAI(unittest.TestCase):
    @patch('ats.agent.tasks.Application.objects.select_related')
    @patch('ats.agent.tasks.analyze_with_deepseek')
    @patch('ats.agent.tasks.extract_text_from_file')
    def test_missing_submission(self, mock_extract, mock_analyze, mock_select_related):
        # Setup mocks
        mock_app = MagicMock()
        mock_app.cv_file = MagicMock()
        mock_app.cover_letter_file = None
        # SIMULATE MISSING SUBMISSION (The core issue)
        mock_app.submission = None
        
        # Configure the chain: Application.objects.select_related(...).get(...)
        mock_queryset = MagicMock()
        mock_queryset.get.return_value = mock_app
        mock_select_related.return_value = mock_queryset

        mock_analyze.return_value = {"score": 50}
        mock_extract.return_value = "Some text"

        # Capture print output to verify the error log
        from io import StringIO
        captured_output = StringIO()
        sys.stdout = captured_output

        # Run the task
        try:
            process_application_ai(123)
        except Exception as e:
            self.fail(f"Task raised exception unexpectedly: {e}")
        finally:
            sys.stdout = sys.__stdout__

        # Check output
        output = captured_output.getvalue()
        print("Captured output:", output)
        self.assertIn("[CELERY ERROR] Application 123 has no linked submission", output)
        self.assertIn("Aborting analysis", output)

if __name__ == '__main__':
    unittest.main()
