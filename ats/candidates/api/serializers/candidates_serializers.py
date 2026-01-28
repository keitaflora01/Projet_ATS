from rest_framework import serializers
from ats.candidates.models.candidates_model import Candidate
from ats.users.models.user_model import User

class CandidateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Candidate
        fields = [
            "id",
            "user",
            "email",
            "full_name",
            "bio",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "user", "created", "modified", "email", "full_name"]

    def update(self, instance, validated_data):
        # Permet de modifier bio uniquement (le reste est read_only)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.save()
        return instance