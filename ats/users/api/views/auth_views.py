import re
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

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
        description="Crée un utilisateur (Candidat ou Recruteur). Pour un recruteur, 'company_name' est requis.",
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
            logger.error("Erreur lors de la création de l'utilisateur %s : %s", request.data.get("email"), str(e), exc_info=True)
            return Response({"detail": "Erreur interne lors de la création."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="Connexion utilisateur",
        description="Authentifie l'utilisateur et retourne les tokens JWT (access + refresh) ainsi que le rôle.",
        request=UserLoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string"},
                    "access": {"type": "string"},
                    "role": {"type": "string"},
                    "user": {"type": "object"} 
                }
            },
            401: "Identifiants invalides",
            400: "Données invalides ou compte désactivé"
        }
    )
    def post(self, request):
        logger.info("Tentative de connexion pour : %s", request.data.get("email"))

        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Erreurs validation login : %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                logger.info("Connexion réussie pour %s", email)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                    "role": user.role
                })
            else:
                logger.warning("Compte désactivé pour %s", email)
                return Response({"detail": "Compte désactivé."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.warning("Échec authentification pour %s", email)
            return Response({"detail": "Email ou mot de passe incorrect."}, status=status.HTTP_401_UNAUTHORIZED)


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
