from rest_framework import serializers
from ats.jobs.models.jobs_model import JobOffer, JobType, ContractType

class JobOfferSerializer(serializers.ModelSerializer):
    recruiter = serializers.PrimaryKeyRelatedField(read_only=True)
    recruiter_company = serializers.CharField(source="recruiter.company_name", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobOffer
        fields = [
            "id",
            "title",
            "description",
            "job_type",
            "contract_type",
            "location",
            "is_remote",
            "salary_min",
            "salary_max",
            "required_skills",
            "requirements",
            "expires_at",
            "is_active",
            "published_at",
            "recruiter",
            "recruiter_company",
            "is_expired",
        ]
        read_only_fields = ["published_at", "is_expired", "recruiter_company"]


    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError({
                "salary_min": "Le salaire minimum ne peut pas être supérieur au maximum."
            })

        recruiter = self.context["request"].user.recruiter_profile
        title = attrs.get("title")
        
        if self.instance:  
            if self.instance.title == title:
                return attrs  
        
        if JobOffer.objects.filter(recruiter=recruiter, title=title).exists():
            raise serializers.ValidationError({
                "title": "Vous avez déjà créé une offre avec ce titre exact."
            })

        return attrs

    def create(self, validated_data):
        recruiter = self.context["request"].user.recruiter_profile
        validated_data["recruiter"] = recruiter
        return super().create(validated_data)
    