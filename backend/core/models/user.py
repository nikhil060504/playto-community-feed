from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds bio field and karma calculation capabilities.
    """
    bio = models.TextField(blank=True, help_text="User biography")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['-date_joined']),
        ]
    
    def __str__(self):
        return self.username
    
    @property
    def total_karma(self):
        """
        Calculate total karma from all time.
        This is computed from Like records, not stored.
        """
        from .like import Like
        return Like.objects.filter(content_author=self).aggregate(
            total=models.Sum('karma_value')
        )['total'] or 0
    
    def karma_last_24h(self):
        """
        Calculate karma earned in the last 24 hours.
        This is the key method used for the leaderboard.
        Returns only karma from likes created in the last 24 hours.
        """
        from django.utils import timezone
        from datetime import timedelta
        from .like import Like
        
        time_threshold = timezone.now() - timedelta(hours=24)
        return Like.objects.filter(
            content_author=self,
            created_at__gte=time_threshold
        ).aggregate(
            total=models.Sum('karma_value')
        )['total'] or 0
