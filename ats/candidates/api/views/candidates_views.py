from ats.candidates.api.serializers.candidates_serializers import CandidateSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.candidates.models.candidates_model import Candidate


class CandidateListView(generics.ListAPIView):
    """
    Lister tous les candidats (admin ou recruteur uniquement)
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role not in ["admin", "recruiter"]:
            return Response({"detail": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)


class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails, modification ou suppression d’un candidat
    - Candidat : peut modifier son propre bio
    - Admin : tout
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        obj = super().get_object()
        if self.request.user.role != "admin" and obj.user != self.request.user:
            self.permission_denied(self.request)
        return obj

    def perform_destroy(self, instance):
        if self.request.user.role != "admin":
            self.permission_denied(self.request)
        instance.delete()