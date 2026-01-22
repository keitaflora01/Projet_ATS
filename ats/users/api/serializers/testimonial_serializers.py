from rest_framework import serializers
from ats.users.models.testimonial_model import Testimonial
from ats.users.api.serializers.user_serializers import UserSerializer
from ats.users.models.user_model import User  

class TestimonialSerializer(serializers.ModelSerializer):
    """
    Serializer complet : renvoie à la fois l'avis ET les infos de l'utilisateur
    """
    user = UserSerializer(read_only=True) 
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "user",
            "user_id",
            "message",
            "rating",
            "is_approved",
            "order",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "created", "modified", "is_approved"]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        if Testimonial.objects.filter(user=self.context['request'].user).exists():
            raise serializers.ValidationError({"detail": "Vous avez déjà laissé un avis."})
        return attrs
    