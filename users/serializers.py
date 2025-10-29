from rest_framework import serializers
from .models import User

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    badge_level = serializers.SerializerMethodField(read_only=True)  # <-- ADD THIS LINE

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'phone', 'role', 'status',
            'profile_photo', 'address', 'badge_level'
        ]
        read_only_fields = ['badge_level', 'id']
        ref_name = 'CustomUserSerializer'

    def get_badge_level(self, obj):
        return obj.badge_level  # Calls your model property


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'password','role']
        extra_kwargs = {"password": {"write_only": True}}
        ref_name = 'CustomUserCreateSerializer'
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)  # Ensure hashing
        user.save()
        return user


# Dashboard Serializer
from rest_framework import serializers
from users.models import User
from upohars.models import UpoharPost, UpoharRequest

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'status', 'total_donations', 'badge_level']

class UpoharPostSerializer(serializers.ModelSerializer):
    donor = BasicUserSerializer()
    receiver = BasicUserSerializer()
    class Meta:
        model = UpoharPost
        fields = ['id', 'title', 'status', 'donor', 'receiver', 'created_at', 'updated_at']

class UpoharRequestSerializer(serializers.ModelSerializer):
    gift = UpoharPostSerializer()
    requester = BasicUserSerializer()
    class Meta:
        model = UpoharRequest
        fields = ['id', 'gift', 'requester', 'status', 'created_at']

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

