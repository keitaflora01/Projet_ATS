
from ats.interviews.api.serializers.entretient_serializers import InterviewSerializer
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ats.interviews.models.interview_model import Interview
from ats.applications.models.applications_model import Application


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
        application_id = self.kwargs.get('application_id')
        if application_id:
            # Directly filter by Application id
            return Interview.objects.filter(application_id=application_id)
        return Interview.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'recruiter':
            raise permissions.PermissionDenied("Seuls les recruteurs peuvent programmer un entretien.")

        recruiter_profile = self.request.user.recruiter_profile

        # Get application from URL parameter (application_id) instead of expecting it in payload
        application_id = self.kwargs.get('application_id')
        if not application_id:
            raise serializers.ValidationError({
                'application_id': "application_id manquant dans l'URL."
            })

        application = get_object_or_404(Application, pk=application_id)

        # Validate ownership of the job offer
        if application.submission.job_offer.recruiter != recruiter_profile:
            raise permissions.PermissionDenied("Cette candidature ne vous appartient pas.")

        # Ensure job_offer is set from the application
        job_offer = application.submission.job_offer

        serializer.save(application=application, job_offer=job_offer)



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
            return Interview.objects.filter(application__submission__job_offer__recruiter__user=user)
        elif user.role == 'candidate':
            return Interview.objects.filter(application__submission__candidate=user)
        return Interview.objects.none()

    def perform_destroy(self, instance):
        if self.request.user.role != 'recruiter' or instance.application.submission.job_offer.recruiter.user != self.request.user:
            self.permission_denied(self.request)
        instance.delete()