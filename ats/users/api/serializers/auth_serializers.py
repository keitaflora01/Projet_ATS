from rest_framework import serializers
from django.db import transaction

from ats.users.models.user_model import User, UserRole
from ats.candidates.models.candidates_model import Candidate
from ats.recruiters.models.recruiters_model import RecruiterProfile


class CandidateProfileSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Candidate
        fields = ("bio",)
        extra_kwargs = {"bio": {"required": False, "allow_blank": True}}


class RecruiterProfileSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = RecruiterProfile
        fields = (
            "company_name",
            "company_website",
            "company_description",
            "company_logo_file",
            "phone",
            "position",
        )
        extra_kwargs = {
            "company_name": {"required": True},
            "company_website": {"required": False},
            "company_description": {"required": False},
            "company_logo_url": {"required": False},
            "phone": {"required": False},
            "position": {"required": False},
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmer le mot de passe")

    profile_photo = serializers.ImageField(
        required=False,
        allow_null=True,
        write_only=True,           
        allow_empty_file=False,
    )

    candidate_profile = CandidateProfileSerializer(required=False, write_only=True)
    recruiter_profile = RecruiterProfileSerializer(required=False, write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
            "role",
            "password",
            "password2",
            "profile_photo",
            "candidate_profile",
            "recruiter_profile",
        )
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

        if role == UserRole.CANDIDATE:
            pass
        elif role == UserRole.RECRUITER:
            recruiter_data = attrs.get("recruiter_profile")
            if not recruiter_data or not recruiter_data.get("company_name"):
                raise serializers.ValidationError({"company_name": "Obligatoire pour un recruteur."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        profile_photo = validated_data.pop("profile_photo", None)

        password = validated_data.pop("password")
        candidate_data = validated_data.pop("candidate_profile", None)
        recruiter_data = validated_data.pop("recruiter_profile", None)
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

            if profile_photo:
                user.profile_photo = profile_photo
                user.save(update_fields=["profile_photo"])

            if role == UserRole.CANDIDATE and candidate_data:
                Candidate.objects.create(user=user, **candidate_data)
            elif role == UserRole.RECRUITER and recruiter_data:
                RecruiterProfile.objects.create(user=user, **recruiter_data)

        return user
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        if not email or not password:
            raise serializers.ValidationError({"detail": "Email et mot de passe requis."})
        return attrs
    