from django.urls import path

from ats.submissions.api.views.submission_views import SubmissionDetailView, SubmissionCreateView, SubmissionListView

urlpatterns = [
    path('api/submissions/', SubmissionListView.as_view(), name='submission-list'),          # ← GET sur cette URL
    path('api/submissions/create/', SubmissionCreateView.as_view(), name='submission-create'),  # ← POST ici (ou sur le même)
    path('api/submissions/<uuid:id>/', SubmissionDetailView.as_view(), name='submission-detail'),
]