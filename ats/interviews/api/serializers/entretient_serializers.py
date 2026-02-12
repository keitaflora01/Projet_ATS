from rest_framework import serializers
from ats.interviews.models.interview_model import Interview
from django.utils import timezone
from django.utils.timezone import localtime


class InterviewSerializer(serializers.ModelSerializer):
    """Serializer matching `ats.interviews.models.interview_model.Interview`.

    Exposes helper display fields (status, candidate name, job title) and
    validates that the authenticated recruiter owns the job offer when creating
    an interview.
    """
    interview_status_display = serializers.SerializerMethodField(read_only=True)
    candidate_name = serializers.SerializerMethodField(read_only=True)
    job_title = serializers.SerializerMethodField(read_only=True)
    scheduled_date = serializers.SerializerMethodField(read_only=True)
    scheduled_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id',
            'answers',
            'scheduled_at',
            'completed_at',
            'status',
            'interview_status_display',
            'scheduled_date',
            'scheduled_time',
            'created',
            'modified',
            'candidate_name',
            'job_title',
        ]
        read_only_fields = ['id', 'created', 'modified', 'interview_status_display', 'candidate_name', 'job_title', 'scheduled_date', 'scheduled_time']

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

    def get_scheduled_date(self, obj):
        """Return the scheduled date portion (YYYY-MM-DD) of scheduled_at in local time."""
        if getattr(obj, 'scheduled_at', None):
            dt = localtime(obj.scheduled_at)
            return dt.date().isoformat()
        return None

    def get_scheduled_time(self, obj):
        """Return the scheduled time portion (HH:MM) of scheduled_at in local time."""
        if getattr(obj, 'scheduled_at', None):
            dt = localtime(obj.scheduled_at)
            return dt.time().strftime('%H:%M')
        return None

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