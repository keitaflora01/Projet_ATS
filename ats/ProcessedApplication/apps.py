from django.apps import AppConfig


class ProcessedapplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Use the full python path to the app package so Django can import it
    name = 'ats.ProcessedApplication'
