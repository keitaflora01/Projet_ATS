from ats.submissions.api.serializers.submissions_serializers import SubmissionCreateSerializer, SubmissionSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.submissions.models.submissions_models import Submission
from ats.applications.models.applications_model import Application
from ats.agent.tasks import process_application_ai
from django.db import transaction


class SubmissionListView(generics.ListAPIView):
    """
    Liste des soumissions visibles pour l'utilisateur connecté
    """
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Submission.objects.all()
        elif user.role == "recruiter":
            return Submission.objects.filter(job_offer__recruiter__user=user)
        elif user.role == "candidate":
            return Submission.objects.filter(candidate=user)
        return Submission.objects.none()

@extend_schema(summary="Liste des candidatures/soumissions")

class SubmissionCreateView(generics.CreateAPIView):
    serializer_class = SubmissionCreateSerializer
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
        
        print(f"✅ Candidature créée !")
        print(f"   → Submission ID: {submission.id}")
        print(f"   → Application ID: {application.id}")
        
        # Lancement IA
        transaction.on_commit(lambda: process_application_ai.delay(application.id))
        print(f"   → Celery Task: process_application_ai triggered")
        
        # Return the submission object for proper serialization
        return submission

    @extend_schema(summary="Créer une candidature")
    def post(self, request, *args, **kwargs):
        if request.user.role != "candidate":
            return Response({"detail": "Seuls les candidats peuvent postuler."}, status=403)
        
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            submission = self.perform_create(serializer)
        
        # Use SubmissionSerializer for response
        response_serializer = SubmissionSerializer(submission)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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
      