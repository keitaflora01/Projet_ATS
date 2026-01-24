from ats.submissions.api.serializers.submissions_serializers import SubmissionCreateSerializer, SubmissionSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.submissions.models.submissions_models import Submission
from ats.agent.tasks import process_application_ai  

class SubmissionCreateView(generics.CreateAPIView):
    serializer_class = SubmissionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Postuler à une offre - créer candidature complète")
    def post(self, request):
        print("\n" + "="*50)
        print("🆕 CANDIDAT POSTULE À UNE OFFRE (API complète)")
        print(f"Utilisateur : {request.user.email} (rôle: {request.user.role})")
        print("Données reçues :", request.data)
        print("Fichiers reçus :", list(request.FILES.keys()))

        if request.user.role != "candidate":
            print("❌ Refus : rôle non candidat")
            return Response({"detail": "Seuls les candidats peuvent postuler."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            result = serializer.save()
            submission = result["submission"]
            application = result["application"]
            
            print(f"✅ Candidature créée !")
            print(f"   → Submission ID: {submission.id}")
            print(f"   → Application ID: {application.id}")
            print(f"   → Offre: {submission.job_offer.title}")
            print(f"   → CV uploadé: {application.cv_file.name}")

            process_application_ai.delay(application.id)
            print(f"[CELERY] Tâche d'analyse IA lancée pour application {application.id}")

            return Response({
                "message": "Postulation réussie ! Votre candidature a été enregistrée.",
                "submission_id": str(submission.id),
                "application_id": str(application.id),
                "job_offer": submission.job_offer.title,
                "status": submission.get_status_display(),
                "cv_url": application.cv_file.url if application.cv_file else None,
                "cover_letter_url": application.cover_letter_file.url if application.cover_letter_file else None
            }, status=status.HTTP_201_CREATED)
        else:
            print("❌ Erreurs :", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class SubmissionListView(generics.ListAPIView):
    """
    Lister toutes les candidatures (recruteur voit celles de ses offres, admin voit tout)
    """
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Submission.objects.all()
        elif user.role == "recruiter":
            return Submission.objects.filter(job_offer__recruiter__user=user)
        else:
            return Submission.objects.filter(candidate=user)

    @extend_schema(summary="Lister les candidatures (filtrées par rôle)")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
      