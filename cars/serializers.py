from rest_framework import serializers
from .models import Car, CarImage, Comment, Rating

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ('id', 'image', 'is_primary')

class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'user_username', 'created_at', 'updated_at')
        read_only_fields = ('user_username',)

class RatingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Rating
        fields = ('id', 'rating', 'user_username', 'created_at')
        read_only_fields = ('user_username',)

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Car
        fields = ('id', 'owner', 'owner_username', 'make', 'model', 'year',
                 'price_per_day', 'description', 'location', 'available',
                 'images', 'comments', 'ratings', 'average_rating',
                 'created_at', 'updated_at')
        read_only_fields = ('owner', 'owner_username', 'average_rating')
