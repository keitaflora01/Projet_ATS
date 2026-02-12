from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ats.interviews.models.interview_model import Interview
from ats.applications.models.applications_model import Application
from ats.interviews.api.serializers.entretient_serializers import InterviewSerializer


class InterviewListCreateView(generics.ListCreateAPIView):
    """
    GET     → Liste des entretiens programmés pour une candidature (via application_id)
    POST    → Créer un nouvel entretien manuel pour une candidature précise
    """
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        application_id = self.kwargs.get('application_id')
        if application_id:
            return Interview.objects.filter(application_id=application_id)
        return Interview.objects.none()

    def perform_create(self, serializer):
        # 1. Vérification rôle recruteur
        if self.request.user.role != 'recruiter':
            raise permissions.PermissionDenied("Seuls les recruteurs peuvent programmer un entretien.")

        recruiter_profile = self.request.user.recruiter_profile

        # 2. Récupération de l'application depuis l'URL (plus fiable que le body)
        application_id = self.kwargs.get('application_id')
        if not application_id:
            raise serializers.ValidationError({
                "application_id": "L'ID de l'application est requis dans l'URL."
            })

        application = get_object_or_404(Application, pk=application_id)

        # 3. Vérification que la candidature appartient à une offre du recruteur
        if application.submission.job_offer.recruiter != recruiter_profile:
            raise permissions.PermissionDenied("Cette candidature ne vous appartient pas.")

        # 4. Sauvegarde en renseignant application et job_offer depuis l'application
        serializer.save(application=application, job_offer=application.submission.job_offer)


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
            # Tous les entretiens liés aux offres du recruteur
            return Interview.objects.filter(application__submission__job_offer__recruiter__user=user)
        elif user.role == 'candidate':
            # Tous les entretiens liés aux candidatures du candidat
            return Interview.objects.filter(application__submission__candidate=user)
        return Interview.objects.none()

    def perform_destroy(self, instance):
        # Seul le recruteur propriétaire de l'offre peut supprimer
        if (self.request.user.role != 'recruiter' or
            instance.application.submission.job_offer.recruiter.user != self.request.user):
            self.permission_denied(self.request)
        instance.delete()
