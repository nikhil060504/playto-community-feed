from django.utils import timezone
from django.db.models import Sum, F
from datetime import timedelta
from core.models import Like, User


def get_top_users_24h(limit=5):
    """
    Calculate top users by karma earned in the last 24 hours.
    
    This is the CRITICAL function for the leaderboard requirement.
    It demonstrates dynamic aggregation from Like history, not stored fields.
    
    The approach:
    1. Filter Like objects created in last 24 hours
    2. Group by content_author (the person receiving karma)
    3. Sum the karma_value field for each author
    4. Order by total karma descending
    5. Limit to top N users
    
    Why this works:
    - Each Like record has created_at timestamp
    - Each Like has karma_value (5 for post, 1 for comment)
    - Each Like has content_author (person who gets the karma)
    - We don't need a separate DailyKarma model or cached field
    
    Performance considerations:
    - Index on (content_author, created_at) makes this fast
    - Even with millions of likes, filtering on timestamp is efficient
    - Aggregation happens in the database, not Python
    
    Args:
        limit: Number of top users to return (default: 5)
    
    Returns:
        QuerySet of User objects with karma_24h annotation
    
    Example SQL this generates (approximately):
        SELECT 
            user.*,
            SUM(like.karma_value) as karma_24h
        FROM user
        INNER JOIN like ON user.id = like.content_author_id
        WHERE like.created_at >= (NOW() - INTERVAL '24 hours')
        GROUP BY user.id
        ORDER BY karma_24h DESC
        LIMIT 5;
    """
    # Calculate timestamp 24 hours ago
    time_threshold = timezone.now() - timedelta(hours=24)
    
    # Get users who have received likes in the last 24h
    # Annotate with sum of karma_value from those likes
    top_users = User.objects.filter(
        likes_received__created_at__gte=time_threshold
    ).annotate(
        karma_24h=Sum('likes_received__karma_value')
    ).order_by('-karma_24h')[:limit]
    
    return top_users
