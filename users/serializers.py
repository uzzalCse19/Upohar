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
            'id', 'name', 'email', 'phone', 'role', 'status','is_superuser',
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
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'phone', 'role', 'status', 'is_staff',
            'is_superuser', 'date_joined', 'profile_photo', 'total_donations'
        ]
        read_only_fields = ['date_joined', 'total_donations']
from upohars.models import UpoharPost, UpoharImage, UpoharRequest
from upohars.models import UpoharPost, UpoharRequest
from upohars.serializers import UpoharPostSerializer, UpoharImageSerializer

class UpoharPostAdminSerializer(serializers.ModelSerializer):
    donor = BasicUserSerializer(read_only=True)
    images = UpoharImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = UpoharPost
        fields = [
            'id', 'title', 'description', 'city', 'type', 'status', 'category',
            'category_name', 'donor', 'receiver', 'exchange_item_name',
            'exchange_item_description', 'image', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['donor', 'created_at', 'updated_at']

class UpoharRequestAdminSerializer(serializers.ModelSerializer):
    gift = UpoharPostAdminSerializer(read_only=True)
    requester = BasicUserSerializer(read_only=True)

    gift_id = serializers.PrimaryKeyRelatedField(
        source='gift', queryset=UpoharPost.objects.all(), write_only=True
    )

    class Meta:
        model = UpoharRequest
        fields = [
            'id', 'gift', 'gift_id', 'requester', 'message', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']