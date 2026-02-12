from rest_framework import serializers
from ats.interviews.models.interview_model import Interview
from django.utils import timezone


class InterviewSerializer(serializers.ModelSerializer):
    """Serializer matching `ats.interviews.models.interview_model.Interview`.

    Exposes helper display fields (status, candidate name, job title) and
    validates that the authenticated recruiter owns the job offer when creating
    an interview.
    """
    interview_status_display = serializers.SerializerMethodField(read_only=True)
    candidate_name = serializers.SerializerMethodField(read_only=True)
    job_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id',
            'application',
            'job_offer',
            'questions',
            'answers',
            'scheduled_at',
            'completed_at',
            'status',
            'interview_status_display',
            'created',
            'modified',
            'candidate_name',
            'job_title',
        ]
        read_only_fields = ['id', 'created', 'modified', 'interview_status_display', 'candidate_name', 'job_title']

    def get_interview_status_display(self, obj):
        try:
            return obj.get_status_display()
        except Exception:
            return None

    def get_candidate_name(self, obj):
        # application -> submission -> candidate
        if getattr(obj, 'application', None) and getattr(obj.application, 'submission', None) and obj.application.submission.candidate:
            return obj.application.submission.candidate.get_full_name() or obj.application.submission.candidate.email
        return "—"

    def get_job_title(self, obj):
        # job_offer exists on the Interview model
        if getattr(obj, 'job_offer', None):
            return obj.job_offer.title
        # fallback to application -> submission -> job_offer
        if getattr(obj, 'application', None) and getattr(obj.application, 'submission', None) and obj.application.submission.job_offer:
            return obj.application.submission.job_offer.title
        return "—"

    def validate_scheduled_at(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("La date d'entretien ne peut pas être dans le passé.")
        return value

    def validate(self, attrs):
        # Ensure recruiter owns the job offer when creating an interview
        request = self.context.get('request')
        if request and request.user and request.user.role == 'recruiter' and 'application' in attrs:
            application = attrs['application']
            recruiter = request.user.recruiter_profile
            if application.submission.job_offer.recruiter != recruiter:
                raise serializers.ValidationError({
                    "application": "Vous n'êtes pas autorisé à programmer un entretien pour cette candidature."
                })
        return attrs