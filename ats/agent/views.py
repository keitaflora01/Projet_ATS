from ats.submissions.models.submissions_models import Submission
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models.analysis_result import AIAnalysisResult
from .serializers import AIAnalysisResultSerializer
from .tasks import process_application_ai
from ats.applications.models.applications_model import Application


class AnalysisListView(generics.ListAPIView):
    """
    Liste toutes les analyses IA pour les candidatures d'une offre (recruteur uniquement)
    """
    serializer_class = AIAnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != "recruiter":
            return AIAnalysisResult.objects.none()

        return AIAnalysisResult.objects.filter(
            submission__job_offer__recruiter__user=user
        ).select_related("submission__job_offer", "submission__candidate")

    @extend_schema(summary="Lister les analyses IA des candidatures (recruteur)")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AnalysisDetailView(generics.RetrieveAPIView):
    """
    Détails d'une analyse IA pour une candidature spécifique
    """
    serializer_class = AIAnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "submission_id"

    def get_queryset(self):
        user = self.request.user
        if user.role != "recruiter":
            return AIAnalysisResult.objects.none()
        return AIAnalysisResult.objects.filter(
            submission__job_offer__recruiter__user=user
        )

    @extend_schema(summary="Détails d'une analyse IA")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ForceAnalysisView(APIView):
    """
    Force le lancement immédiat de l'analyse IA pour une candidature (recruteur ou admin)
    Utile pour tester ou relancer si Celery a échoué
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Forcer l'analyse IA d'une candidature")
    def post(self, request, submission_id):
        user = request.user
        if user.role not in ["recruiter", "admin"]:
            return Response({"detail": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)

        try:
            submission = Submission.objects.get(id=submission_id)
            if user.role == "recruiter" and submission.job_offer.recruiter.user != user:
                return Response({"detail": "Vous n'êtes pas le recruteur de cette offre"}, status=403)

            if hasattr(submission, 'application'):
                app_id = submission.application.id
                process_application_ai.delay(app_id)  
                return Response({
                    "message": "Analyse IA relancée avec succès (en background)",
                    "submission_id": str(submission_id)
                }, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"detail": "Aucune application associée à cette candidature"}, status=400)

        except Submission.DoesNotExist:
            return Response({"detail": "Candidature non trouvée"}, status=404)
        