from django.contrib import admin
from core.models import User, Post, Comment, Like


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model"""
    list_display = ['username', 'email', 'total_karma', 'date_joined']
    search_fields = ['username', 'email']
    list_filter = ['date_joined']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model"""
    list_display = ['id', 'author', 'content_preview', 'like_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']
    raw_id_fields = ['author']
    
    def content_preview(self, obj):
        """Show first 50 characters of content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model"""
    list_display = ['id', 'author', 'post', 'parent', 'depth', 'like_count', 'created_at']
    list_filter = ['created_at', 'depth']
    search_fields = ['content', 'author__username']
    raw_id_fields = ['author', 'post', 'parent']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin interface for Like model"""
    list_display = ['id', 'user', 'content_type', 'object_id', 'content_author', 'karma_value', 'created_at']
    list_filter = ['created_at', 'karma_value', 'content_type']
    search_fields = ['user__username', 'content_author__username']
    raw_id_fields = ['user', 'content_author']
