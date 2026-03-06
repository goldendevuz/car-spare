from rest_framework import serializers
from .models import City, Shop, Part, Feedback


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name"]


class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name", "phone", "city", "latitude", "longitude", "landmark", "status", "seller_token"]
        read_only_fields = ["id", "status", "seller_token"]


class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ["id", "shop", "car_model", "name", "price", "in_stock", "created_at"]
        read_only_fields = ["id", "created_at"]


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "telegram_id", "role", "city", "message", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]