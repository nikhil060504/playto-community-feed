# Make views directory a Python package
from .auth_views import RegisterView, CurrentUserView
from .post_views import PostViewSet
from .comment_views import CommentViewSet
from .leaderboard_views import LeaderboardView

__all__ = [
    'RegisterView',
    'CurrentUserView',
    'PostViewSet',
    'CommentViewSet',
    'LeaderboardView',
]
