from django.urls import path
from ats.candidates.api.views.candidates_views import CandidateDetailView, CandidateListView


urlpatterns = [
    path("api/candidates/", CandidateListView.as_view(), name="candidate-list"),
    path("api/candidates/<uuid:pk>/", CandidateDetailView.as_view(), name="candidate-detail"),
]
