from ats.applications.api import serializers
from .models.analysis_result import AIAnalysisResult


class AIAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisResult
        fields = [
            "id",
            "submission",
            "score",
            "extracted_skills",
            "matching_skills",
            "missing_skills",
            "summary",
            "recommendation",
            "confidence",
            "processed_at",
        ]
        read_only_fields = fields  
        