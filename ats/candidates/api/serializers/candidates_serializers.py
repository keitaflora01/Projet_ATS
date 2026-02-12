from rest_framework import serializers
from ats.candidates.models.candidates_model import Candidate
from ats.users.models.user_model import User

class CandidateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            "id",
            "user",
            "email",
            "full_name",
            "bio",
            "profile_photo_url",     
            "created",
            "modified",
        ]
        read_only_fields = ["id", "user", "created", "modified", "email", "full_name", "profile_photo_url"]

    def update(self, instance, validated_data):
        # Permet de modifier bio uniquement (le reste est read_only)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.save()
        return instance

    def get_profile_photo_url(self, obj):
        if getattr(obj, "profile_photo", None):
            return obj.profile_photo.url if obj.profile_photo else None
        if getattr(obj.user, "profile_photo", None):
            return obj.user.profile_photo.url if obj.user.profile_photo else None
        return None