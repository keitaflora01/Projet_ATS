from rest_framework import serializers
from django.db import transaction
from ats.users.models.user_model import User, UserRole
from ats.candidates.models.candidates_model import Candidate
from ats.recruiters.models.recruiters_model import RecruiterProfile

Recruiter = RecruiterProfile

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmer le mot de passe", style={"input_type": "password"})
    
    # Champ optionnel pour les recruteurs
    company_name = serializers.CharField(write_only=True, required=False, label="Nom de l'entreprise (Recruteurs uniquement)")

    class Meta:
        model = User
        fields = ("email", "full_name", "role", "password", "password2", "company_name")
        extra_kwargs = {
            "email": {"required": True},
            "role": {"required": True},
        }

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        
        role = attrs.get("role")
        if role not in [choice[0] for choice in UserRole.choices]:
            raise serializers.ValidationError({"role": "Rôle invalide."})
            
        if role == UserRole.RECRUITER and not attrs.get("company_name"):
            raise serializers.ValidationError({"company_name": "Le nom de l'entreprise est obligatoire pour un compte recruteur."})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        company_name = validated_data.pop("company_name", None)
        role = validated_data.get("role")
        
        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data["email"],
                full_name=validated_data.get("full_name", ""),
                role=role,
                password=password,
            )
            user.is_verified = False
            user.save()

            if role == UserRole.CANDIDATE:
                Candidate.objects.create(user=user)
            elif role == UserRole.RECRUITER:
                Recruiter.objects.create(user=user, company_name=company_name)
            
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})
