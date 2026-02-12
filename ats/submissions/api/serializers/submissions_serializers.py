from rest_framework import serializers
from ats.jobs.api.serializers.jops_serializers import JobOfferSerializer
from ats.submissions.models.submissions_models import Submission
from ats.applications.models.applications_model import Application
from ats.applications.api.serializers.applications_serializers import ApplicationSerializer
from ats.users.api.serializers.user_serializers import UserSerializer  # pour les fichiers

class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour lister / détailler une candidature
    """
    candidate = UserSerializer(read_only=True)
    job_offer = JobOfferSerializer(read_only=True)
    application = ApplicationSerializer(read_only=True)  # Inclut CV, LM, score IA, resume, statut
   
    # Retourne le résumé généré par l'IA pour l'application associée (si présent)
    ai_summary = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Submission
        fields = [
            "id",
            "candidate",
            "job_offer",
            'ai_summary',
            "status",
            "application",
            "created",
        ]
        read_only_fields = ["id", "created"]

    def get_ai_summary(self, obj):
        """Récupère le champ `resume` de l'Application liée à cette Submission.

        Si l'application n'existe pas ou que `resume` est vide, retourne None.
        """
        try:
            application = getattr(obj, 'application', None)
            if application and getattr(application, 'resume', None):
                return application.resume
        except Exception:
            pass
        return None
class SubmissionCreateSerializer(serializers.Serializer):
    job_offer_id = serializers.UUIDField(required=True)
    cover_letter_text = serializers.CharField(required=False, allow_blank=True)
    
    years_experience = serializers.IntegerField(required=False, allow_null=True)
    availability_date = serializers.DateField(required=False, allow_null=True)
    desired_salary = serializers.DecimalField(required=False, allow_null=True, max_digits=12, decimal_places=2)
    portfolio_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    cv_file = serializers.FileField(required=True)
    cover_letter_file = serializers.FileField(required=False)
    other_documents = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_job_offer_id(self, value):
        from ats.jobs.models.jobs_model import JobOffer
        try:
            offer = JobOffer.objects.get(id=value, is_active=True)
        except JobOffer.DoesNotExist:
            raise serializers.ValidationError("Offre non trouvée ou inactive.")
        return value

    def create(self, validated_data):
        job_offer_id = validated_data.pop("job_offer_id")
        from ats.jobs.models.jobs_model import JobOffer
        job_offer = JobOffer.objects.get(id=job_offer_id)

        candidate = self.context["request"].user

        if candidate.role != "candidate":
            raise serializers.ValidationError("Seuls les candidats peuvent postuler.")

        submission = Submission.objects.create(
            candidate=candidate,
            job_offer=job_offer
        )

        application_data = {
            "submission": submission,
            "years_experience": validated_data.pop("years_experience", None),
            "availability_date": validated_data.pop("availability_date", None),
            "desired_salary": validated_data.pop("desired_salary", None),
            "portfolio_url": validated_data.pop("portfolio_url", None),
            "other_documents": validated_data.pop("other_documents", None),
            "cv_file": validated_data.pop("cv_file"),
            "cover_letter_file": validated_data.pop("cover_letter_file", None),
        }
        application = Application.objects.create(**application_data)

        return {
            "submission": submission,
            "application": application
        }
    
