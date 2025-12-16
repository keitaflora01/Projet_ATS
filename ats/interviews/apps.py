from django.apps import AppConfig


class InterviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Use the full Python path to the application so Django can import it
    name = 'ats.interviews'
