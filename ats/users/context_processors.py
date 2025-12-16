from django.conf import settings


def allauth_settings(request):
    """Expose some settings from django-allauth in templates."""
    """Return empty dict for compatibility.

    Replace with real context data if you restore template-based flows.
    """
    return {}
