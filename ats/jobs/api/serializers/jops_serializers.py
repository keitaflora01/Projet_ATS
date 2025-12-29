# ats/jobs/api/serializers/jobs_serializers.py
from rest_framework import serializers
from ats.jobs.models.jobs_model import JobOffer, JobType
# from ats.recruiters.api.serializers.recruiter_serializers import RecruiterSerializer  # si tu en as un, sinon on peut simplifier

class JobOfferSerializer(serializers.ModelSerializer):
    recruiter = serializers.PrimaryKeyRelatedField(read_only=True)  # Le recruteur est défini automatiquement
    recruiter_company = serializers.CharField(source="recruiter.company_name", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobOffer
        fields = [
            "id",
            "title",
            "description",
            "requirements",
            "responsibilities",
            "location",
            "is_remote",
            "job_type",
            "salary_min",
            "salary_max",
            "expires_at",
            "is_active",
            "published_at",
            "recruiter",
            "recruiter_company",
            "is_expired",
        ]
        read_only_fields = ["published_at", "is_expired", "recruiter_company"]

    def validate(self, attrs):
        # Validation personnalisée si besoin (ex: salary_min < salary_max)
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError({"salary_min": "Le salaire minimum ne peut pas être supérieur au maximum."})
        return attrs