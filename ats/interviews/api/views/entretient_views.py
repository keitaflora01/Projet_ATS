
from ats.interviews.api.serializers.entretient_serializers import InterviewSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ats.interviews.models.interview_model import Interview


class InterviewListCreateView(generics.ListCreateAPIView):
    """
    GET     → Liste des entretiens programmés pour une candidature
    POST    → Créer un nouvel entretien manuel
    """
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()] 
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        submission_id = self.kwargs.get('submission_id')
        if submission_id:
            return Interview.objects.filter(submission_id=submission_id)
        return Interview.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'recruteur':
            raise permissions.PermissionDenied("Seuls les recruteurs peuvent programmer un entretien.")
        
        recruiter_profile = self.request.user.recruteur_profile   
        submission = serializer.validated_data['submission']
        
        if submission.job_offer.recruteur != recruiter_profile:
            raise permissions.PermissionDenied("Cette candidature ne vous appartient pas.")
        
        serializer.save()



class InterviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → Détails d'un entretien
    PUT    → Remplacer entièrement un entretien
    PATCH  → Modifier partiellement
    DELETE → Supprimer un entretien
    """
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'recruiter':
            return Interview.objects.filter(submission__job_offer__recruiter__user=user)
        elif user.role == 'candidate':
            return Interview.objects.filter(submission__candidate=user)
        return Interview.objects.none()

    def perform_destroy(self, instance):
        if self.request.user.role != 'recruiter' or instance.submission.job_offer.recruiter.user != self.request.user:
            self.permission_denied(self.request)
        instance.delete()