from rest_framework import serializers
from ats.users.models.user_model import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "role", "is_active", "is_verified", "created")
        read_only_fields = ("id", "created")
