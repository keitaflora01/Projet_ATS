# ats/interviews/api/urls.py
from django.urls import path
from .views import InterviewQuestionsView

urlpatterns = [
    path('questions/application/<uuid:application_id>/', InterviewQuestionsView.as_view(), name='interview-questions-by-app'),
    path('questions/<uuid:pk>/', InterviewQuestionsView.as_view(), name='interview-questions-detail'),
]
