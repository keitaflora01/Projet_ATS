# ats/applications/api/views/applications_views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.applications.api.serializers.applications_serializers import ApplicationSerializer
from ats.applications.models.applications_model import Application


class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Uploader CV et lettre de motivation pour une candidature")
    def post(self, request, *args, **kwargs):
        print("\n" + "="*60)
        print("🆕 NOUVELLE REQUÊTE D'UPLOAD DE CANDIDATURE")
        print("="*60)
        print(f"Utilisateur authentifié : {request.user.email} (ID: {request.user.id})")
        print(f"Rôle : {getattr(request.user, 'role', 'Inconnu')}")
        print("Fichiers reçus :", list(request.FILES.keys()))
        print("Données reçues (form) :", request.data)

        # Afficher les fichiers uploadés
        if 'cv_file' in request.FILES:
            cv = request.FILES['cv_file']
            print(f"📄 CV reçu : {cv.name} ({cv.size} bytes)")
        else:
            print("⚠️ Aucun CV reçu")

        if 'cover_letter_file' in request.FILES:
            cl = request.FILES['cover_letter_file']
            print(f"✉️ Lettre de motivation reçue : {cl.name} ({cl.size} bytes)")
        else:
            print("ℹ️ Aucune lettre de motivation")

        serializer = self.get_serializer(data=request.data)
        print("Serializer initialisé")

        if serializer.is_valid():
            print("✅ Serializer valide !")
            try:
                application = serializer.save()
                print(f"🎉 Candidature sauvegardée avec succès ! ID: {application.id}")
                print(f"   → CV stocké : {application.cv_file.url if application.cv_file else 'Non'}")
                print(f"   → Lettre stockée : {application.cover_letter_file.url if application.cover_letter_file else 'Non'}")

                return Response({
                    "message": "Candidature envoyée avec succès !",
                    "cv": application.cv_file.url if application.cv_file else None,
                    "cover_letter": application.cover_letter_file.url if application.cover_letter_file else None,
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"❌ Erreur lors de la sauvegarde : {str(e)}")
                return Response({"detail": "Erreur lors de l'enregistrement."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print("❌ Erreurs de validation du serializer :")
            for field, errors in serializer.errors.items():
                print(f"   → {field}: {errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)