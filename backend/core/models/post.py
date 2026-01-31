from django.db import models
from django.conf import settings


class Post(models.Model):
    """
    Post model representing a text post in the community feed.
    Each post has an author, content, and tracks like counts.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Author of the post"
    )
    content = models.TextField(help_text="Post content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Denormalized field for performance
    # Updated via signals when likes are created/deleted
    like_count = models.IntegerField(
        default=0,
        help_text="Number of likes on this post"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        # Return first 50 chars of content
        return f"{self.author.username}: {self.content[:50]}..."
