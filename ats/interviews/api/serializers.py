from rest_framework import serializers
from ats.interviews.models.interview_model import Interview, InterviewStatus

class InterviewQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['id', 'questions', 'status', 'scheduled_at']

class InterviewAnswerSerializer(serializers.Serializer):
    """
    Utilisé pour POST/PATCH des réponses
    """
    answers = serializers.JSONField(
        help_text="Dictionnaire {numéro_question: réponse}"
    )


class InterviewDetailSerializer(serializers.ModelSerializer):
    """
    Pour GET /interviews/<id>/ → questions + réponses + status
    """
    is_completed = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Interview
        fields = [
            'id',
            'questions',
            'answers',
            'status',
            'scheduled_at',
            'completed_at',
            'is_completed',  
        ]
        read_only_fields = ['id', 'scheduled_at', 'completed_at', 'is_completed']

    def get_is_completed(self, obj):
        """Return True when interview is completed (status==COMPLETED or completed_at set)."""
        if obj is None:
            return False
        return bool(obj.completed_at) or (getattr(obj, 'status', None) == InterviewStatus.COMPLETED)


class CandidateInterviewListSerializer(serializers.ModelSerializer):
    """
    Pour la liste des entretiens d'un candidat
    """
    job_title = serializers.CharField(source='application.job_offer.title', read_only=True)
    is_completed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id',
            'job_title',
            'status',
            'scheduled_at',
            'completed_at',
            'is_completed',
        ]

    def get_is_completed(self, obj):
        if obj is None:
            return False
        return bool(obj.completed_at) or (getattr(obj, 'status', None) == InterviewStatus.COMPLETED)