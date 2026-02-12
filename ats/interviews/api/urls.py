from django.urls import path

from ats.interviews.api.views.entretient_views import InterviewListCreateView
from ats.interviews.api.views.interviews_views import CandidateInterviewAnswersListView, InterviewAnswerCreateUpdateView, InterviewDetailView, InterviewQuestionsView

urlpatterns = [
    # path('questions/application/<uuid:application_id>/', InterviewQuestionsView.as_view(), name='interview-questions-by-app'),
    # path('questions/<uuid:pk>/', InterviewQuestionsView.as_view(), name='interview-questions-detail'),
    # path('candidate/me/answers/', CandidateInterviewAnswersListView.as_view(), name='candidate-interviews-list'),
    # path('<uuid:id>/', InterviewDetailView.as_view(), name='interview-detail'),
    # path('<uuid:id>/answers/', InterviewAnswerCreateUpdateView.as_view(), name='interview-submit-answers'),
    # path('application/<uuid:application_id>/interviews/', InterviewListCreateView.as_view(), name='interview-list-create'),

    # path('interviews/<uuid:id>/', InterviewDetailView.as_view(), name='interview-detail'),

    # 1. Questions d'entretien (générées IA)
    path('questions/application/<uuid:application_id>/', InterviewQuestionsView.as_view(), name='interview-questions-by-app'),
    path('questions/<uuid:pk>/', InterviewQuestionsView.as_view(), name='interview-questions-detail'),

    # 2. Liste des réponses / entretiens du candidat connecté
    path('candidate/me/answers/', CandidateInterviewAnswersListView.as_view(), name='candidate-interviews-list'),

    # 3. Soumettre ou modifier les réponses à un entretien
    path('<uuid:id>/answers/', InterviewAnswerCreateUpdateView.as_view(), name='interview-submit-answers'),

    # 4. Liste + création d'entretiens (plus de submission_id dans l'URL)
    path('interviews/', InterviewListCreateView.as_view(), name='interview-list-create'),

    # 5. Détail, modification, suppression d'un entretien (un seul chemin)
    path('interviews/<uuid:id>/', InterviewDetailView.as_view(), name='interview-detail'),
]

