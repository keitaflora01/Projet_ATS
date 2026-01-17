from django.urls import path
from .views import AnalysisListView, AnalysisDetailView, ForceAnalysisView

urlpatterns = [
    path("api/analyses/", AnalysisListView.as_view(), name="analysis-list"),
    path("api/analyses/<uuid:submission_id>/", AnalysisDetailView.as_view(), name="analysis-detail"),
    path("api/analyses/<uuid:submission_id>/force/", ForceAnalysisView.as_view(), name="analysis-force"),
]
