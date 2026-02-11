from datetime import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from ats.interviews.models.interview_model import Interview
from ats.interviews.api.serializers import CandidateInterviewListSerializer, InterviewAnswerSerializer, InterviewDetailSerializer, InterviewQuestionsSerializer

class InterviewQuestionsView(generics.RetrieveAPIView):
    """
    Endpoint pour récupérer les questions d'entretien générées par l'IA.
    Accessible par le candidat propriétaire ou le recruteur.
    """
    queryset = Interview.objects.all()
    serializer_class = InterviewQuestionsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'recruiter':
            return Interview.objects.filter(job_offer__recruiter__user=user)
        return Interview.objects.filter(application__submission__candidate=user)

    def get(self, request, *args, **kwargs):
        try:
            application_id = self.kwargs.get('application_id')
            if application_id:
                interview = self.get_queryset().get(application_id=application_id)
                return Response({
                    "id": interview.id,
                    "questions": interview.questions,
                    "status": interview.status
                })
            return super().get(request, *args, **kwargs)
        except Interview.DoesNotExist:
            return Response({"error": "Entretien non trouvé ou accès refusé."}, status=404)

class CandidateInterviewAnswersListView(generics.ListAPIView):
    """
    GET /interviews/candidate/me/answers/
    → Renvoie la liste de tous les entretiens du candidat + statut + si répondu
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CandidateInterviewListSerializer

    def get_queryset(self):
        return Interview.objects.filter(
            application__submission__candidate=self.request.user
        ).select_related('application__job_offer')



class InterviewDetailView(generics.RetrieveAPIView):
    """
    GET /interviews/<uuid:id>/
    → Renvoie questions + réponses + status
    """
    queryset = Interview.objects.all()
    serializer_class = InterviewDetailSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'recruiter':
            return Interview.objects.filter(job_offer__recruiter__user=user)
        return Interview.objects.filter(application__submission__candidate=user)



class InterviewAnswerCreateUpdateView(generics.UpdateAPIView):
    """
    POST / PATCH  /interviews/<uuid:interview_id>/answers/
    Body: { "answers": { "1": "ma réponse...", "2": "autre..." } }
    """
    queryset = Interview.objects.all()
    serializer_class = InterviewAnswerSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Seulement les entretiens du candidat connecté
        return Interview.objects.filter(
            application__submission__candidate=self.request.user
        )

    def update(self, request, *args, **kwargs):
        interview = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data.get('answers', {})

        interview.answers = answers
        interview.status = "completed"
        interview.completed_at = timezone.now()
        interview.save(update_fields=['answers', 'status', 'completed_at'])

        return Response({
            "message": "Réponses enregistrées avec succès",
            "interview_id": str(interview.id),
            "status": interview.status
        }, status=status.HTTP_200_OK)