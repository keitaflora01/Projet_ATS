# ats/agent/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from ats.submissions.models.submission_model import Submission
from .models.analysis_result import AIAnalysisResult
from .serializers import AIAnalysisResultSerializer
from .tasks import process_application_ai


class AnalysisListView(generics.ListAPIView):
    serializer_class = AIAnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "recruiter":
            return AIAnalysisResult.objects.none()
        return AIAnalysisResult.objects.filter(submission__job_offer__recruiter__user=self.request.user)

    @extend_schema(summary="Lister analyses IA (recruteur)")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AnalysisDetailView(generics.RetrieveAPIView):
    serializer_class = AIAnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "submission_id"

    def get_queryset(self):
        if self.request.user.role != "recruiter":
            return AIAnalysisResult.objects.none()
        return AIAnalysisResult.objects.filter(submission__job_offer__recruiter__user=self.request.user)

    @extend_schema(summary="Détails analyse IA")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ForceAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Forcer analyse IA")
    def post(self, request, submission_id):
        if request.user.role != "recruiter":
            return Response({"detail": "Accès refusé"}, status=403)

        try:
            submission = Submission.objects.get(id=submission_id)
            if submission.job_offer.recruiter.user != request.user:
                return Response({"detail": "Non votre offre"}, status=403)

            app = submission.application
            process_application_ai.delay(app.id)
            return Response({"message": "Analyse relancée", "submission_id": submission_id}, status=202)
        except Submission.DoesNotExist:
            return Response({"detail": "Candidature introuvable"}, status=404)