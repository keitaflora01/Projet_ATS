from django.urls import path

from ats.interviews.api.views.entretient_views import InterviewListCreateView
from ats.interviews.api.views.interviews_views import CandidateInterviewAnswersListView, InterviewAnswerCreateUpdateView, InterviewDetailView, InterviewQuestionsView

urlpatterns = [
    path('questions/application/<uuid:application_id>/', InterviewQuestionsView.as_view(), name='interview-questions-by-app'),
    path('questions/<uuid:pk>/', InterviewQuestionsView.as_view(), name='interview-questions-detail'),
    path('candidate/me/answers/', CandidateInterviewAnswersListView.as_view(), name='candidate-interviews-list'),
    path('<uuid:id>/', InterviewDetailView.as_view(), name='interview-detail'),
    path('<uuid:id>/answers/', InterviewAnswerCreateUpdateView.as_view(), name='interview-submit-answers'),
    path('submission/<uuid:submission_id>/interviews/', InterviewListCreateView.as_view(), name='interview-list-create'),

    path('interviews/<uuid:id>/', InterviewDetailView.as_view(), name='interview-detail'),
]

