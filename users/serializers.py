from rest_framework import serializers
from .models import User


# Main User Serializer (for profile, get/update, admin)
class UserSerializer(serializers.ModelSerializer):
    badge_level = serializers.SerializerMethodField(read_only=True)

    class Meta:
        profile_photo = serializers.ImageField(allow_null=True, required=False  ) 
        model = User
        ref_name="UserSerializer"
        fields = [
            'id', 'name', 'email', 'phone', 'role', 'status',
            'profile_photo', 'address', 'total_donations', 'badge_level'
        ]
        read_only_fields = ['id', 'badge_level', 'total_donations']

    def get_badge_level(self, obj):
        return obj.badge_level

# For signup/registration (create-only)
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        ref_name="UserCreateSerializer"
        fields = ['email', 'name', 'phone', 'password', 'role']
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Basic User info for dashboard/child serializations
class BasicUserSerializer(serializers.ModelSerializer):
    badge_level = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'status', 'total_donations', 'badge_level']

    def get_badge_level(self, obj):
        return obj.badge_level


# Optional: For analytics/statistics (custom API endpoints)
class AnalyticsSummarySerializer(serializers.Serializer):
    total_active_users = serializers.IntegerField()
    total_donors = serializers.IntegerField()
    total_receivers = serializers.IntegerField()
    total_upohar_posts = serializers.IntegerField()
    total_completed_posts = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    total_pending = serializers.IntegerField()
    total_approved = serializers.IntegerField()
    total_rejected = serializers.IntegerField()
