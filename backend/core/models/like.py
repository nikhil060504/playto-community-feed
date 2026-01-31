from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class Like(models.Model):
    """
    Like model - the heart of the karma system.
    
    This model tracks ALL likes with timestamps, which allows us to:
    1. Calculate 24-hour karma dynamically (no stored fields needed)
    2. Prevent double-likes with database constraints
    3. Store karma value for easy aggregation
    
    Uses Generic Relations to handle both Post and Comment likes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes_given',
        help_text="User who gave the like"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the like was created (critical for 24h leaderboard)"
    )
    
    # Generic relation - can point to either Post or Comment
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type of content being liked (Post or Comment)"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID of the liked object"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Store the author of the liked content for efficient karma queries
    # This denormalization is critical for leaderboard performance
    content_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes_received',
        help_text="Author of the content that was liked (receives karma)"
    )
    
    # Store karma value (5 for post, 1 for comment)
    # This makes aggregation queries much simpler
    karma_value = models.IntegerField(
        help_text="Karma points awarded (5 for post like, 1 for comment like)"
    )
    
    class Meta:
        # Critical: prevent double-likes at database level
        # This handles race conditions - only one like per user per content
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'],
                name='unique_like_per_user_per_content'
            )
        ]
        indexes = [
            # For leaderboard queries - get karma by author in last 24h
            models.Index(fields=['content_author', '-created_at']),
            # For checking if user already liked something
            models.Index(fields=['user', 'content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} liked {self.content_type} (karma: {self.karma_value})"
