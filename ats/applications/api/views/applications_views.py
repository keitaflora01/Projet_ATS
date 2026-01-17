import traceback
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ats.applications.api.serializers.applications_serializers import ApplicationSerializer
from ats.applications.models.applications_model import Application

from ats.agent.tasks import process_application_ai


class ApplicationCreateView(generics.CreateAPIView):
    """
    Vue API pour créer une candidature complète :
    - Informations personnelles (expérience, salaire, disponibilité, portfolio)
    - Fichiers uploadés (CV obligatoire, LM optionnel)
    - Lance automatiquement l'analyse IA en background via Celery
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Créer une candidature complète + lancement analyse IA automatique")
    def post(self, request, *args, **kwargs):
        print("\n" + "="*70)
        print("🆕 NOUVELLE REQUÊTE DE CRÉATION DE CANDIDATURE")
        print("="*70)
        print(f"Utilisateur : {request.user.email} (ID: {request.user.id})")
        print(f"Rôle : {getattr(request.user, 'role', 'Inconnu')}")
        print("Données reçues (form) :", dict(request.data))  
        print("Fichiers reçus :", list(request.FILES.keys()))

        if 'cv_file' in request.FILES:
            cv = request.FILES['cv_file']
            print(f"📄 CV reçu : {cv.name} ({cv.size:,} bytes, type: {cv.content_type})")
        else:
            print("⚠️ Aucun CV reçu (champ obligatoire)")

        if 'cover_letter_file' in request.FILES:
            cl = request.FILES['cover_letter_file']
            print(f"✉️ Lettre de motivation reçue : {cl.name} ({cl.size:,} bytes)")
        else:
            print("ℹ️ Aucune lettre de motivation (optionnel)")

        serializer = self.get_serializer(data=request.data, context={'request': request})
        print("Serializer initialisé")

        if serializer.is_valid():
            print("✅ Serializer valide !")
            try:
                application = serializer.save()
                print(f"🎉 Candidature sauvegardée avec succès ! ID: {application.id}")
                print(f"   → Années d'expérience : {application.years_experience}")
                print(f"   → Date disponibilité : {application.availability_date}")
                print(f"   → Salaire souhaité : {application.desired_salary} €")
                print(f"   → Portfolio : {application.portfolio_url or 'Non renseigné'}")
                print(f"   → CV stocké : {application.cv_file.url if application.cv_file else 'Non'}")
                print(f"   → Lettre stockée : {application.cover_letter_file.url if application.cover_letter_file else 'Non'}")
                print(f"   → Score IA initial : {application.ia_score}")


                process_application_ai.delay(application.id)
                print(f"[CELERY] Tâche d'analyse IA lancée pour application {application.id}")

                return Response({
                    "message": "Candidature envoyée avec succès ! L'analyse IA est en cours (résultats visibles dans l'admin après traitement)...",
                    "application_id": application.id,
                    "submission_id": application.submission.id,
                    "cv_url": application.cv_file.url if application.cv_file else None,
                    "cover_letter_url": application.cover_letter_file.url if application.cover_letter_file else None,
                    "portfolio_url": application.portfolio_url,
                    "score_ia_initial": application.ia_score,
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f"❌ Erreur lors de la sauvegarde : {str(e)}")
                traceback.print_exc()  
                
                return Response({"detail": "Erreur lors de l'enregistrement de la candidature."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            print("❌ Erreurs de validation du serializer :")
            for field, errors in serializer.errors.items():
                print(f"   → {field}: {errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        