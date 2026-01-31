from django.db import models
from django.conf import settings


class Comment(models.Model):
    """
    Comment model with simple threading support.
    Uses adjacency list pattern (self-referential foreign key).
    Tracks depth to keep nesting simple and UI-friendly.
    """
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Post this comment belongs to"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Author of the comment"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text="Parent comment for threading (null for top-level comments)"
    )
    content = models.TextField(help_text="Comment content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Depth tracking for simple nesting UI
    # Level 0 = top-level, Level 1 = reply to top-level, etc.
    depth = models.IntegerField(
        default=0,
        help_text="Nesting depth (0 for root comments)"
    )
    
    # Denormalized field for performance
    like_count = models.IntegerField(
        default=0,
        help_text="Number of likes on this comment"
    )
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'parent']),  # For fetching comment trees
            models.Index(fields=['created_at']),
            models.Index(fields=['author']),
        ]
    
    def save(self, *args, **kwargs):
        """
        Auto-calculate depth based on parent.
        This keeps the depth field in sync automatically.
        """
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"
