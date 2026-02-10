from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.users.api.serializers.testimonial_serializers import TestimonialSerializer
from ats.users.models.testimonial_model import Testimonial


class TestimonialListCreateView(generics.ListCreateAPIView):
    """
    - GET : Lister tous les avis approuvés (public)
    - POST : Créer un nouvel avis (utilisateur connecté)
    """
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]  

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.request.method == 'GET':
            return Testimonial.objects.filter(is_approved=True).order_by('order', '-created')
        return Testimonial.objects.filter(user=self.request.user)

    @extend_schema(summary="Lister les avis approuvés ou créer un avis")
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated]
            self.check_permissions(request)
        return super().post(request, *args, **kwargs)


class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET : Détails d'un avis
    - PATCH : Modifier son propre avis
    - DELETE : Supprimer son propre avis (ou admin)
    """
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.user and self.request.user.role != "admin":
            self.permission_denied(self.request)
        return obj

    @extend_schema(summary="Détails, modification ou suppression d'un avis")
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if self.request.user != instance.user and self.request.user.role != "admin":
            self.permission_denied(self.request)
        instance.delete()
