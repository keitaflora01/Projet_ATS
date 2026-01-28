import os
import sys
import django

# Add project root to sys.path
sys.path.append("/home/keita/ats")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ats.applications.models.applications_model import Application
from ats.submissions.models.submissions_models import Submission

print("DEBUG: Checking recent Applications...")
try:
    apps = Application.objects.select_related('submission').order_by('-created')[:5]
    for app in apps:
        print(f"App ID: {app.id}")
        print(f"  Submission ID attribute: {app.submission_id}")
        try:
            print(f"  Submission linked: {app.submission}")
            print(f"  Job Offer: {app.submission.job_offer}")
        except Exception as e:
            print(f"  Error accessing submission: {e}")
except Exception as e:
    print(f"Error querying applications: {e}")
