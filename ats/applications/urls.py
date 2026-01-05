# ats/applications/urls.py
from django.urls import path
from .api.views.applications_views import ApplicationCreateView

urlpatterns = [
    path("api/applications/", ApplicationCreateView.as_view(), name="application-create"),
]