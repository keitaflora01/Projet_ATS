from rest_framework import serializers
from ats.users.models.user_model import User

class UserSerializer(serializers.ModelSerializer):
    profile_photo_url = serializers.SerializerMethodField()  

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "role",
            "is_active",
            "is_verified",
            "created",
            "profile_photo_url",  
        )
        read_only_fields = ("id", "created", "profile_photo_url")

    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            return obj.profile_photo.url
        return None  