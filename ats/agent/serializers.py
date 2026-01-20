from rest_framework import serializers
from .models.analysis_result import AIAnalysisResult


class AIAnalysisResultSerializer(serializers.ModelSerializer):
    recommendation_display = serializers.CharField(source="get_recommendation_display", read_only=True)

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
            "recommendation_display",
            "confidence",
            "processed_at",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["status"] = instance.status if hasattr(instance, 'status') else "pending"
        return rep
    