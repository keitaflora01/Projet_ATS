from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ats.users.api.serializers.user_serializers import UserSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(f"\n=== ACCÈS AU PROFIL === Utilisateur : {request.user.email}")
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
