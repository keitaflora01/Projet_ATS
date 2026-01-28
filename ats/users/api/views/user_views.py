from ats.users.api.serializers.user_serializers import UserListSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from ats.users.models.user_model import User
from ats.users.api.serializers.user_serializers import UserListSerializer, UserUpdateSerializer, UserSerializer


class UserListView(generics.ListAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Accès réservé aux administrateurs"}, status=403)
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateAPIView):
   
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return UserSerializer
        return UserUpdateSerializer

    def get_object(self):
        obj = super().get_object()
        if obj != self.request.user and self.request.user.role != 'admin':
            self.permission_denied(self.request)
        return obj

    @extend_schema(summary="Récupérer ou modifier un utilisateur")
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Modifier complètement un utilisateur (PUT)")
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class UserProfileView(APIView):
   
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=400)