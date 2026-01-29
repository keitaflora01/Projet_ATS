from django.urls import path

from ats.submissions.api.views.submission_views import SubmissionDetailView, SubmissionCreateView

urlpatterns = [
    path('api/submissions/', SubmissionCreateView.as_view(), name="submission-create"),
    path('api/submissions/<uuid:id>/', SubmissionDetailView.as_view(), name='submission-detail'),
]