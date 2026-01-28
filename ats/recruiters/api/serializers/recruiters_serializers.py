# ats/recruiters/api/serializers/recruiters_serializers.py
from rest_framework import serializers
from ats.recruiters.models.recruiters_model import RecruiterProfile
from ats.users.models.user_model import User

class RecruiterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)

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
            "company_logo_url",
            "phone",
            "position",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "user", "created", "modified", "email", "full_name"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance