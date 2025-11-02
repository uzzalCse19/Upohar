from rest_framework import serializers
from .models import Category, UpoharPost, UpoharImage, UpoharRequest
from rest_framework import serializers
from .models import UpoharRequest, UpoharPost

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active']

class UpoharImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # 🔹 use method

    class Meta:
        model = UpoharImage
        fields = ['id', 'image', 'is_primary', 'uploaded_at']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url  # 🔹 important for CloudinaryField
        return None


from rest_framework import serializers
from .models import UpoharPost, Category, UpoharImage


class UpoharPostSerializer(serializers.ModelSerializer):
    donor = serializers.SerializerMethodField()
    receiver = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    primary_image = serializers.SerializerMethodField()  # 🔹 new

    class Meta:
        model = UpoharPost
        fields = [
            'id', 'donor', 'receiver', 'category', 'type', 'exchange_item_name', 'exchange_item_description',
            'title', 'description', 'city', 'image', 'primary_image', 'images',
            'status', 'created_at', 'updated_at'
        ]

    def get_donor(self, obj):
        if obj.donor:
            return obj.donor.name if obj.donor.name else obj.donor.email
        return None

    def get_primary_image(self, obj):
        # return first primary image or fallback to post.image
        primary = obj.images.filter(is_primary=True).first()
        if primary and primary.image:
            return primary.image.url
        elif obj.image:
            return obj.image.url
        return None
       
    
from users.models import User






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


# class UpoharPostSerializer(serializers.ModelSerializer):
#     donor = serializers.SerializerMethodField()
#     receiver = serializers.StringRelatedField(read_only=True)
#     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
#     images = UpoharImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = UpoharPost
#         fields = [
#             'id', 'donor', 'receiver', 'category', 'type', 'exchange_item_name', 'exchange_item_description',
#             'title', 'description', 'city', 'image', 'images',
#             'status', 'created_at', 'updated_at'
#         ]

#     def get_donor(self, obj):
#         if obj.donor:
#             return obj.donor.name if obj.donor.name else obj.donor.email
#         return None