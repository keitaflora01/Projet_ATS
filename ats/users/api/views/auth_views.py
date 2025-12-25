import re
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from ats.users.api.serializers.auth_serializers import UserRegisterSerializer, UserLoginSerializer
from ats.users.api.serializers.user_serializers import UserSerializer

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

    def post(self, request):
        print("\n=== REQUÊTE D'INSCRIPTION RECEIVED ===")
        print("Données reçues :", request.data)

        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            print("Erreurs de validation serializer :", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        password = serializer.validated_data["password"]
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            print("Mot de passe faible :", message)
            return Response({"password": [message]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            print(f"Utilisateur créé avec succès : {user.email} (rôle: {user.role})")
            return Response({
                "user": UserSerializer(user).data,
                "message": "Utilisateur créé avec succès. Vous pouvez maintenant vous connecter."
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Erreur lors de la création de l'utilisateur :", str(e))
            return Response({"detail": "Erreur interne lors de la création."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("\n=== REQUÊTE DE CONNEXION RECEIVED ===")
        print("Données reçues :", request.data)

        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            print("Erreurs serializer login :", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        print(f"Tentative de connexion avec email : {email}")

        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                print(f"Connexion réussie pour {email}")
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                    "role": user.role
                })
            else:
                print(f"Compte désactivé : {email}")
                return Response({"detail": "Compte désactivé."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"Échec authentification pour {email} - mauvais email/mot de passe")
            return Response({"detail": "Email ou mot de passe incorrect."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("\n=== REQUÊTE DE DÉCONNEXION ===")
        print("Utilisateur :", request.user.email if request.user else "Anonyme")
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            print("Token mis en blacklist - Déconnexion réussie")
            return Response({"message": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print("Erreur lors de la déconnexion :", str(e))
            return Response({"detail": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST)
