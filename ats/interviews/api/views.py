# ats/interviews/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from ats.interviews.models.interview_model import Interview
from ats.interviews.api.serializers import InterviewQuestionsSerializer

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
            # On cherche par application_id ou interview_id
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
