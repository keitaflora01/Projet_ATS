from django.urls import path

from ats.submissions.api.views.submission_views import SubmissionDetailView, SubmissionListCreateView
# from ats.submissions.api.views.submission_views import SubmissionCreateView, SubmissionDetailView, SubmissionListView

urlpatterns = [
    path("api/submissions/", SubmissionListCreateView.as_view(), name="submission-list-create"),
    path('api/submissions/<uuid:id>/', SubmissionDetailView.as_view(), name='submission-detail'),
]