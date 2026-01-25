from rest_framework import serializers
from ats.users.models.user_model import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "role",
            "is_active",
            "is_verified",
            "profile_photo",
            "profile_photo_url",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "profile_photo_url")

    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            return obj.profile_photo.url
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
  
    profile_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "full_name",
            "profile_photo",
            "email",  
            "role",   
        )
        read_only_fields = ("email", "role")  

    def update(self, instance, validated_data):
        if self.context['request'].user.role == 'admin':
            instance.email = validated_data.get('email', instance.email)
            instance.role = validated_data.get('role', instance.role)
        
        instance.full_name = validated_data.get('full_name', instance.full_name)
        if 'profile_photo' in validated_data:
            instance.profile_photo = validated_data['profile_photo']
        
        instance.save()
        return instance


class UserListSerializer(UserSerializer):
  
    class Meta(UserSerializer.Meta):
        fields = ("id", "email", "full_name", "role", "profile_photo_url", "date_joined")