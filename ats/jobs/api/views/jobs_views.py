import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.jobs.api.serializers.jops_serializers import JobOfferSerializer
from ats.jobs.models.jobs_model import JobOffer

logger = logging.getLogger(__name__)

class IsOwnerRecruiter(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(f"🔐 Vérification permission : user={request.user.email if request.user.is_authenticated else 'Anonyme'}, "
              f"offre recruteur={obj.recruiter.user.email}")
        return obj.recruiter.user == request.user


class JobOfferListCreateView(generics.ListCreateAPIView):
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.AllowAny] # Allow viewing jobs publicly

    def get_queryset(self):
        if self.request.user.is_authenticated:
            print(f"👀 Récupération des offres pour l'utilisateur : {self.request.user.email}")
        else:
            print("👀 Récupération des offres pour un visiteur anonyme")
        if getattr(self.request.user, "role", None) == "recruiter":
            qs = JobOffer.objects.filter(recruiter__user=self.request.user)
            print(f"   → Recruteur : {qs.count()} offre(s) trouvée(s)")
            return qs
        # Candidats et admin voient les offres actives
        qs = JobOffer.objects.filter(is_active=True)
        print(f"   → Public : {qs.count()} offre(s) active(s)")
        return qs

    @extend_schema(summary="Lister les offres ou en créer une nouvelle (recruteur uniquement)")
    def post(self, request, *args, **kwargs):
        print("\n🆕 REQUÊTE DE CRÉATION D'OFFRE REÇUE")
        print("Utilisateur authentifié :", request.user.email if request.user.is_authenticated else "Aucun")
        print("Rôle de l'utilisateur :", getattr(request.user, "role", "Inconnu"))
        print("Données reçues :", request.data)

        # Vérification rôle recruteur
        if getattr(request.user, "role", None) != "recruiter":
            print("❌ Refus : l'utilisateur n'est pas un recruteur")
            return Response(
                {"detail": "Seuls les recruteurs peuvent créer des offres."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Récupération du profil recruteur
        try:
            recruiter = request.user.recruiter_profile
            print(f"✅ Profil recruteur trouvé : {recruiter.company_name}")
        except AttributeError:
            print("❌ Erreur : aucun profil recruteur associé à cet utilisateur")
            return Response(
                {"detail": "Profil recruteur non trouvé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        print("Serializer initialisé")

        if serializer.is_valid():
            print("✅ Serializer valide, sauvegarde en cours...")
            job_offer = serializer.save(recruiter=recruiter)
            print(f"🎉 Offre créée avec succès ! ID: {job_offer.id} - Titre: {job_offer.title}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("❌ Erreurs de validation du serializer :")
            for field, errors in serializer.errors.items():
                print(f"   - {field}: {errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobOfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return JobOffer.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"👁️ Consultation de l'offre ID={instance.id} par {request.user.email}")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        print(f"\n✏️ REQUÊTE DE MISE À JOUR de l'offre {kwargs.get('id')}")
        print("Données envoyées :", request.data)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        print(f"\n🩹 REQUÊTE PATCH (mise à jour partielle) de l'offre {kwargs.get('id')}")
        print("Données envoyées :", request.data)
        return super().partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        print("Sauvegarde des modifications...")
        serializer.save()
        print("✅ Offre mise à jour avec succès")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"🗑️ Suppression de l'offre {instance.id} par {request.user.email}")
        return super().destroy(request, *args, **kwargs)