# ats/interviews/api/serializers.py
from rest_framework import serializers
from ats.interviews.models.interview_model import Interview

class InterviewQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['id', 'questions', 'status', 'scheduled_at']
