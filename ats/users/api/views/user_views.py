import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from ats.users.api.serializers.user_serializers import UserSerializer

logger = logging.getLogger(__name__)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Profil utilisateur",
        description="Récupère les informations du profil de l'utilisateur connecté.",
        responses={200: UserSerializer}
    )
    def get(self, request):
        logger.info("Consultation profil par : %s", request.user.email)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
