from ats.recruiters.api.serializers.recruiters_serializers import RecruiterSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.recruiters.models.recruiters_model import RecruiterProfile


class RecruiterListView(generics.ListAPIView):
    """
    Lister tous les recruteurs (admin uniquement)
    """
    queryset = RecruiterProfile.objects.all()
    serializer_class = RecruiterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response({"detail": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)


class RecruiterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails, modification ou suppression d’un recruteur
    - Recruteur : peut modifier son propre profil
    - Admin : tout
    """
    queryset = RecruiterProfile.objects.all()
    serializer_class = RecruiterSerializer
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