from ats.recruiters.models.recruiters_model import RecruiterProfile
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

    display_name = serializers.SerializerMethodField(read_only=True)
    company_name = serializers.SerializerMethodField(read_only=True)
    profile_photo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "user",
            "user_id",
            "display_name",         
            "company_name",
            "profile_photo_url",          
            "message",
            "rating",
            "is_approved",
            "order",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "created", "modified", "is_approved", "display_name", "company_name", "profile_photo_url"]
    
    def get_display_name(self, obj):
        return obj.user.get_full_name() or obj.user.email
    
    def get_profile_photo_url(self, obj):
        if obj.user.profile_photo and hasattr(obj.user.profile_photo, 'url'):
            return obj.user.profile_photo.url
        return None

    def get_company_name(self, obj):
        if obj.user.role == "recruiter":
            try:
                profile = obj.user.recruiter_profile
                return profile.company_name if profile.company_name else None
            except RecruiterProfile.DoesNotExist:
                return None
        return None
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        if Testimonial.objects.filter(user=self.context['request'].user).exists():
            raise serializers.ValidationError({"detail": "Vous avez déjà laissé un avis."})
        return attrs
    