from ats.submissions.models.submissions_models import Submission
from rest_framework import serializers

class SubmissionCreateSerializer(serializers.ModelSerializer):
    job_offer_id = serializers.UUIDField(write_only=True)  # L'ID de l'offre

    class Meta:
        model = Submission
        fields = ["job_offer_id", "cover_letter"]  
        extra_kwargs = {
            "cover_letter": {"required": False, "allow_blank": True}
        }

    def validate_job_offer_id(self, value):
        from ats.jobs.models.jobs_model import JobOffer
        try:
            JobOffer.objects.get(id=value, is_active=True)
        except JobOffer.DoesNotExist:
            raise serializers.ValidationError("Offre non trouvée ou inactive.")
        return value

    def create(self, validated_data):
        job_offer_id = validated_data.pop("job_offer_id")
        from ats.jobs.models.jobs_model import JobOffer
        job_offer = JobOffer.objects.get(id=job_offer_id)

        candidate = self.context["request"].user.candidate_profile  # à adapter si tu as un CandidateProfile

        submission = Submission.objects.create(
            candidate=candidate,
            job_offer=job_offer,
            cover_letter=validated_data.get("cover_letter", "")
        )
        return submission