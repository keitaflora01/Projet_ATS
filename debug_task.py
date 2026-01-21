
import os
import django
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ats.applications.models.applications_model import Application
from ats.agent.tasks import process_application_ai

def debug_task():
    print("--- DEBUGGING TASK ---")
    
    # Check Env
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        print(f"✅ DEEPSEEK_API_KEY found (length: {len(key)})")
    else:
        print("❌ DEEPSEEK_API_KEY NOT FOUND in os.environ")
        # Try loading from .env via django-environ manually if needed, 
        # but django.setup() should have handled it if settings.py does it.
    
    try:
        latest_app = Application.objects.latest('created')
        print(f"Latest Application ID: {latest_app.id}")
        
        print("Running task synchronously...")
        # Call the function directly, bypassing Celery broker
        process_application_ai(latest_app.id)
        
        print("Task execution finished.")
        
    except Application.DoesNotExist:
        print("❌ No application found.")
    except Exception as e:
        print(f"❌ Exception during task execution: {e}")

if __name__ == "__main__":
    debug_task()
