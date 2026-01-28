from ats.submissions.api.serializers.submissions_serializers import SubmissionCreateSerializer, SubmissionSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.submissions.models.submissions_models import Submission
from ats.submissions.api.serializers.submissions_serializers import SubmissionCreateSerializer, SubmissionSerializer
from ats.agent.tasks import process_application_ai  

class SubmissionListCreateView(generics.ListCreateAPIView):
    """
    - GET : Lister les candidatures (filtré par rôle)
    - POST : Créer une nouvelle candidature + lancer analyse IA
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubmissionCreateSerializer
        return SubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Submission.objects.all()
        elif user.role == "recruiter":
            return Submission.objects.filter(job_offer__recruiter__user=user)
        else:  # candidate
            return Submission.objects.filter(candidate=user)

    def perform_create(self, serializer):
        result = serializer.save()
        submission = result["submission"]
        application = result["application"]
        
        print(f"[DEBUG] Candidature créée - Submission ID: {submission.id}, Application ID: {application.id}")
        
        # Lancement IA
        process_application_ai.delay(application.id)
        print(f"[CELERY] Tâche d'analyse IA lancée pour application {application.id}")

    @extend_schema(summary="Lister ou créer une candidature")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary="Lister ou créer une candidature")
    def post(self, request, *args, **kwargs):
        if request.user.role != "candidate":
            return Response({"detail": "Seuls les candidats peuvent postuler."}, status=403)
        return super().post(request, *args, **kwargs)


class SubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'une candidature + suppression (admin ou recruteur de l'offre)
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Submission.objects.all()
        elif user.role == "recruiter":
            return Submission.objects.filter(job_offer__recruiter__user=user)
        elif user.role == "candidate":
            return Submission.objects.filter(candidate=user)
        return Submission.objects.none()

    def perform_destroy(self, instance):
        if self.request.user.role not in ["admin", "recruiter"] or (
            self.request.user.role == "recruiter" and instance.job_offer.recruiter.user != self.request.user
        ):
            self.permission_denied(self.request)
        instance.delete()

    @extend_schema(summary="Détails d'une candidature + suppression")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)      
      