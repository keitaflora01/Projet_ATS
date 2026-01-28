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
            "years_experience",
            "availability_date",
            "desired_salary",
            "portfolio_url",
            "cv_file",
            "cover_letter_file",
            "other_documents",
            "ia_score",
        ]
        read_only_fields = ["id", "ia_score"]  

    def validate(self, attrs):
        submission = attrs.get("submission")
        # Vérifie que la candidature appartient au candidat connecté
        if submission.candidate.user != self.context["request"].user:
            raise serializers.ValidationError("Vous ne pouvez pas candidater à cette offre.")
        return attrs