from rest_framework import serializers
from core.models import Post
from .auth_serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying posts.
    Includes author details and like information.
    """
    author = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'content',
            'like_count',
            'is_liked',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'like_count', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        """Check if current user has liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from core.models import Like
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(Post)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new posts.
    Author is set automatically from request user.
    """
    class Meta:
        model = Post
        fields = ['content']
    
    def create(self, validated_data):
        """Set author from request user"""
        request = self.context.get('request')
        validated_data['author'] = request.user
        return super().create(validated_data)
