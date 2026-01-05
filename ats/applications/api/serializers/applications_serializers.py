# ats/applications/api/serializers/applications_serializers.py
from rest_framework import serializers

from ats.applications.models.applications_model import Application

class ApplicationSerializer(serializers.ModelSerializer):
    cv_file = serializers.FileField(required=True)
    cover_letter_file = serializers.FileField(required=False)
    
    class Meta:
        model = Application
        fields = [
            "id",
            "submission",
            "cv_file",
            "cover_letter_file",
            "portfolio_url",
            "other_documents",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        submission = attrs.get("submission")
        # Vérifier que la candidature appartient au candidat connecté
        if submission.candidate.user != self.context["request"].user:
            raise serializers.ValidationError("Vous ne pouvez pas candidater à cette offre.")
        return attrs