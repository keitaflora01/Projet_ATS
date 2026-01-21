
import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ats.applications.models.applications_model import Application
from ats.agent.models.analysis_result import AIAnalysisResult

def verify_latest_submission():
    print("\n--- Verifying Latest AI Analysis Result ---")
    
    # Get the most recent application
    try:
        latest_app = Application.objects.latest('created')
        print(f"Latest Application ID: {latest_app.id}")
        
        # Check if CV text was extracted (we can't check the file content easily but we can check if analysis ran)
        # Check for Analysis Result
        try:
            analysis = AIAnalysisResult.objects.get(submission=latest_app.submission)
            print("✅ Analysis Result Found!")
            print(f"   Score: {analysis.score}")
            print(f"   Recommendation: {analysis.recommendation}")
            print(f"   Confidence: {analysis.confidence}")
            print(f"   Skills Extracted: {analysis.extracted_skills}")
            print(f"   Summary: {analysis.summary[:200]}...") # Print first 200 chars
            
            if analysis.score > 0 and analysis.extracted_skills:
                 print("✅ VERIFICATION SUCCESS: AI analysis produced valid results.")
            else:
                 print("⚠️ LOW/EMPTY SCORE: Analysis might have failed to extract text.")

        except AIAnalysisResult.DoesNotExist:
            print("❌ No Analysis Result found for this application.")
            
    except Application.DoesNotExist:
        print("❌ No applications found in the database.")

if __name__ == "__main__":
    verify_latest_submission()
