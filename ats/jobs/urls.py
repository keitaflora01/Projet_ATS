# ats/jobs/urls.py (ou api/urls.py)
from django.urls import path
from .api.views.jobs_views import JobOfferListCreateView, JobOfferRetrieveUpdateDestroyView

urlpatterns = [
    path("api/offers/", JobOfferListCreateView.as_view(), name="joboffer-list-create"),
    path("api/offers/<uuid:id>/", JobOfferRetrieveUpdateDestroyView.as_view(), name="joboffer-detail"),
]