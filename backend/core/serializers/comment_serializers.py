from rest_framework import serializers
from core.models import Comment
from .auth_serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying comments with nested replies.
    Supports simple threading with depth tracking.
    """
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author',
            'parent',
            'content',
            'depth',
            'like_count',
            'is_liked',
            'replies',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'depth', 'like_count', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """
        Recursively serialize replies.
        Only go a few levels deep to keep it simple.
        """
        # Limit nesting depth in serialization to avoid deeply nested JSON
        if obj.depth >= 3:
            return []
        
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data
    
    def get_is_liked(self, obj):
        """Check if current user has liked this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from core.models import Like
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(Comment)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new comments.
    Author is set automatically from request user.
    """
    class Meta:
        model = Comment
        fields = ['post', 'parent', 'content']
    
    def validate(self, attrs):
        """
        Validate that parent comment belongs to the same post.
        Also limit nesting depth for better UX.
        """
        parent = attrs.get('parent')
        post = attrs.get('post')
        
        if parent:
            if parent.post != post:
                raise serializers.ValidationError({
                    'parent': 'Parent comment must belong to the same post'
                })
            
            # Limit depth to keep UI simple
            if parent.depth >= 4:
                raise serializers.ValidationError({
                    'parent': 'Comment nesting is too deep (max 5 levels)'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Set author from request user"""
        request = self.context.get('request')
        validated_data['author'] = request.user
        return super().create(validated_data)
