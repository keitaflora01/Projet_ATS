from django.urls import path
from ats.submissions.api.views.submission_views import SubmissionCreateView

urlpatterns = [
    path("api/submissions/", SubmissionCreateView.as_view(), name="submission-create"),
]