# ats/submissions/api/views/submission_views.py
from ats.submissions.api.serializers.submissions_serializers import SubmissionCreateSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.submissions.models.submissions_models import Submission

class SubmissionCreateView(generics.CreateAPIView):
    serializer_class = SubmissionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Postuler à une offre d'emploi")
    def post(self, request):
        print("\n" + "="*50)
        print("🆕 CANDIDAT POSTULE À UNE OFFRE")
        print(f"Utilisateur : {request.user.email} (rôle: {request.user.role})")
        print("Données reçues :", request.data)

        if request.user.role != "candidate":
            return Response({"detail": "Seuls les candidats peuvent postuler."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            submission = serializer.save()
            print(f"✅ Candidature créée ! ID: {submission.id} pour l'offre {submission.job_offer.title}")
            return Response({
                "message": "Postulation réussie !",
                "submission_id": str(submission.id),
                "job_offer": submission.job_offer.title
            }, status=status.HTTP_201_CREATED)
        print("❌ Erreurs :", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)