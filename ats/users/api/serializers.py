# ats/users/api/serializers.py
from rest_framework import serializers
from ats.users.models.user_model import User, UserRole

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmer le mot de passe", style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("email", "full_name", "role", "password", "password2")
        extra_kwargs = {
            "email": {"required": True},
            "role": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        if attrs["role"] not in [choice[0] for choice in UserRole.choices]:
            raise serializers.ValidationError({"role": "Rôle invalide."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data.get("full_name", ""),
            role=validated_data["role"],
            password=validated_data["password"],
        )
        user.is_verified = False  # Optionnel : tu peux envoyer un email de vérification plus tard
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "role", "is_active", "is_verified", "created_at")
        read_only_fields = ("id", "created_at")