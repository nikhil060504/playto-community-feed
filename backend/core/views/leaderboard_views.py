from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from core.services import get_top_users_24h
from core.serializers import LeaderboardUserSerializer


class LeaderboardView(APIView):
    """
    API endpoint for the leaderboard.
    GET /api/leaderboard/
    
    This is the CRITICAL endpoint that demonstrates dynamic 24h karma calculation.
    
    Returns: Top 5 users by karma earned in last 24 hours.
    
    The implementation:
    - Uses get_top_users_24h service which aggregates from Like records
    - NO stored "daily_karma" field on User model
    - Calculates dynamically from created_at timestamps on Likes
    - Efficient thanks to database indexes on (content_author, created_at)
    
    For the EXPLAINER.md, the QuerySet used is:
    ```python
    User.objects.filter(
        likes_received__created_at__gte=timezone.now() - timedelta(hours=24)
    ).annotate(
        karma_24h=Sum('likes_received__karma_value')
    ).order_by('-karma_24h')[:5]
    ```
    """
    permission_classes = [permissions.AllowAny]  # Public leaderboard
    
    def get(self, request):
        """Return top 5 users by 24h karma"""
        top_users = get_top_users_24h(limit=5)
        serializer = LeaderboardUserSerializer(top_users, many=True)
        return Response(serializer.data)
