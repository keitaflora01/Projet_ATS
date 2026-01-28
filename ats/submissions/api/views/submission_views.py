# ats/submissions/api/views/submission_views.py
from ats.submissions.api.serializers.submissions_serializers import SubmissionCreateSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.agent.tasks import process_application_ai
from django.db import transaction

# 
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
            with transaction.atomic():
                result = serializer.save()
                submission = result["submission"]
                application = result["application"]
                
                # Trigger Celery Task safely on commit
                transaction.on_commit(lambda: process_application_ai.delay(application.id))

            print(f"✅ Candidature créée !")
            print(f"   → Submission ID: {submission.id}")
            print(f"   → Application ID: {application.id}")
            print(f"   → Celery Task: process_application_ai triggered")

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
        