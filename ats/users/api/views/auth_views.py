import re
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiTypes, OpenApiExample
import logging

from ats.users.api.serializers.auth_serializers import UserRegisterSerializer, UserLoginSerializer
from ats.users.api.serializers.user_serializers import UserSerializer

logger = logging.getLogger(__name__)

def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères."
    if not re.search(r"[a-zA-Z]", password):
        return False, "Le mot de passe doit contenir au moins une lettre."
    if not re.search(r"[0-9]", password):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    return True, "OK"


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer  

    @extend_schema(
        summary="Enregistrer un nouvel utilisateur",
        description="Crée un utilisateur (Candidat ou Recruteur). Les champs supplémentaires dépendent du rôle.",
        request=UserRegisterSerializer,
        responses={201: UserSerializer, 400: "Erreur de validation"}
    )
    def post(self, request):
        logger.info("Requête d'inscription reçue : %s", request.data.get("email"))

        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Erreurs de validation inscription : %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        password = serializer.validated_data["password"]
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            logger.warning("Mot de passe faible pour %s : %s", request.data.get("email"), message)
            return Response({"password": [message]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            logger.info("Utilisateur créé avec succès : %s (rôle: %s)", user.email, user.role)
            return Response({
                "user": UserSerializer(user).data,
                "message": "Utilisateur créé avec succès. Vous pouvez maintenant vous connecter."
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Erreur lors de la création : %s", str(e), exc_info=True)
            return Response({"detail": "Erreur interne lors de la création."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="Connexion utilisateur",
        description=(
            "Authentifie l'utilisateur et retourne les tokens JWT (access + refresh) "
            "ainsi que les informations enrichies de l'utilisateur, incluant les IDs "
            "des profils candidat et recruteur associés (s'ils existent)."
        ),
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Connexion réussie",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        name="Exemple de connexion réussie (candidat)",
                        summary="Réponse typique pour un candidat",
                        description="Tokens + données utilisateur enrichies",
                        value={
                            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "user": {
                                "id": 123,
                                "email": "ktprincesse@gmail.com",
                                "full_name": "Princess KT",
                                "role": "candidate",
                                "is_verified": False,
                                "candidate_profile_id": 45,
                                "recruiter_profile_id": None
                            }
                        },
                        media_type="application/json",
                    ),
                  
                ]
            ),
            400: OpenApiResponse(description="Données invalides ou compte désactivé"),
            401: OpenApiResponse(description="Identifiants invalides"),
        }
    )
    def post(self, request):
        logger.info("Tentative de connexion pour : %s", request.data.get("email"))

        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Erreurs de validation login : %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(email=email, password=password)
        if user is None:
            logger.warning("Échec authentification pour %s", email)
            return Response(
                {"detail": "Email ou mot de passe incorrect."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            logger.warning("Compte désactivé pour %s", email)
            return Response(
                {"detail": "Compte désactivé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        candidate_profile_id = None
        recruiter_profile_id = None

        try:
            if hasattr(user, 'candidate_profile') and user.candidate_profile:
                candidate_profile_id = user.candidate_profile.id
        except Exception:
            pass

        try:
            if hasattr(user, 'recruiter_profile') and user.recruiter_profile:
                recruiter_profile_id = user.recruiter_profile.id
        except Exception:
            pass

        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name or "",
            "role": user.role,
            "is_verified": user.is_verified,
            "candidate_profile_id": candidate_profile_id,
            "recruiter_profile_id": recruiter_profile_id,
        }

        logger.info(
            "Connexion réussie pour %s (role: %s, candidate_id: %s, recruiter_id: %s)",
            email, user.role, candidate_profile_id, recruiter_profile_id
        )

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data
        }, status=status.HTTP_200_OK)   
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Déconnexion",
        description="Blacklist le refresh token fourni.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string"}
                },
                "required": ["refresh"]
            }
        },
        responses={205: "Déconnexion réussie", 400: "Token invalide"}
    )
    def post(self, request):
        logger.info("Requête de déconnexion pour : %s", request.user.email)
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("Token blacklisté pour %s", request.user.email)
            return Response({"message": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error("Erreur déconnexion pour %s : %s", request.user.email, str(e))
            return Response({"detail": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST)
