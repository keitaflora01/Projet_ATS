from rest_framework import serializers
from ats.recruiters.models.recruiters_model import RecruiterProfile
from ats.users.models.user_model import User
 

class RecruiterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = RecruiterProfile
        fields = [
            "id",
            "user",
            "email",
            "full_name",
            "company_name",
            "company_website",
            "company_description",
            "company_logo_file",
            "phone",
            "position",
            "profile_photo_url",      
            "created",
            "modified",
        ]
        read_only_fields = ["id", "user", "created", "modified", "email", "full_name", "profile_photo_url"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_profile_photo_url(self, obj):
        # Prefer profile photo on the RecruiterProfile model, fallback to user's profile photo
        if getattr(obj, "profile_photo", None):
            return obj.profile_photo.url if obj.profile_photo else None
        if getattr(obj.user, "profile_photo", None):
            return obj.user.profile_photo.url if obj.user.profile_photo else None
        return None