from rest_framework import serializers
from ats.interviews.models.interview_model import Interview, InterviewStatus
from django.utils import timezone


class InterviewSerializer(serializers.ModelSerializer):
    interview_type_display = serializers.CharField(source='get_interview_type_display', read_only=True)
    interview_status_display = serializers.CharField(source='get_interview_status_display', read_only=True)
    candidate_name = serializers.SerializerMethodField(read_only=True)
    job_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id',
            'submission',                    
            'interview_type',
            'interview_type_display',
            'scheduled_at',
            'location_or_link',
            'notes',
            'interview_status',
            'interview_status_display',
            'created',
            'modified',
            'candidate_name',
            'job_title',
        ]
        read_only_fields = ['id', 'created', 'modified', 'interview_type_display', 'interview_status_display', 'candidate_name', 'job_title']

    def get_candidate_name(self, obj):
        if obj.submission and obj.submission.candidate:
            return obj.submission.candidate.get_full_name() or obj.submission.candidate.email
        return "—"

    def get_job_title(self, obj):
        if obj.submission and obj.submission.job_offer:
            return obj.submission.job_offer.title
        return "—"

    def validate_scheduled_at(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("La date d'entretien ne peut pas être dans le passé.")
        return value

    def validate(self, attrs):
        if 'submission' in attrs:
            submission = attrs['submission']
            recruiter = self.context['request'].user.recruteur_profile  
            if submission.job_offer.recruter != recruiter:  
                raise serializers.ValidationError({
                    "submission": "Vous n'êtes pas autorisé à programmer un entretien pour cette candidature."
                })
        return attrs