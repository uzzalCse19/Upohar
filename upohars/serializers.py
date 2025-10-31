from rest_framework import serializers
from .models import Category, UpoharPost, UpoharImage, UpoharRequest

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active']

class UpoharImageSerializer(serializers.ModelSerializer):
    image=serializers.ImageField()
    class Meta:
        model = UpoharImage
        fields = ['id', 'image', 'is_primary', 'uploaded_at']

from rest_framework import serializers
from .models import UpoharPost, Category, UpoharImage

class UpoharPostSerializer(serializers.ModelSerializer):
    donor = serializers.SerializerMethodField()
    receiver = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    images = UpoharImageSerializer(many=True, read_only=True)

    class Meta:
        model = UpoharPost
        fields = [
            'id', 'donor', 'receiver', 'category', 'type', 'exchange_item_name', 'exchange_item_description',
            'title', 'description', 'city', 'image', 'images',
            'status', 'created_at', 'updated_at'
        ]

    def get_donor(self, obj):
        if obj.donor:
            return obj.donor.name if obj.donor.name else obj.donor.email
        return None

        
    
from users.models import User



from rest_framework import serializers
from .models import UpoharRequest, UpoharPost


class UpoharRequestSerializer(serializers.ModelSerializer):
    gift = serializers.PrimaryKeyRelatedField(queryset=UpoharPost.objects.all())
    requester = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UpoharRequest
        fields = [
            'id', 'gift', 'requester', 'message', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status']

    def get_gift(self, obj):
        return obj.gift.title if obj.gift else None

    def get_requester(self, obj):
        if obj.requester:
            return getattr(obj.requester, 'name', obj.requester.email)
        return None


# class UpoharRequestSerializer(serializers.ModelSerializer):
#     gift = serializers.PrimaryKeyRelatedField(queryset=UpoharPost.objects.all())  # 🔹 writable
#     requester = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = UpoharRequest
#         fields = [
#             'id', 'gift', 'requester', 'message', 'status', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['created_at', 'updated_at', 'status']

#     def get_gift(self, obj):
#         return obj.gift.title if obj.gift else None

#     def get_requester(self, obj):
#         if obj.requester:
#             return obj.requester.name if obj.requester.name else obj.requester.email
#         return None