from django.apps import AppConfig


class RecruitersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # full dotted path so Django imports the package correctly
    name = 'ats.recruiters'
