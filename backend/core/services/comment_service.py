from django.db.models import Prefetch
from core.models import Comment


def get_post_comments_tree(post):
    """
    Fetch all comments for a post with their nested replies efficiently.
    
    This solves the N+1 query problem for comment threading.
    
    The challenge:
    - Without optimization, fetching 50 nested comments triggers 50+ queries
    - Each comment.author access = 1 query
    - Each comment.replies access = 1 query
    - Total: 1 + 50 + 50 = 101 queries!
    
    The solution:
    - Use select_related() to join user data in one query
    - Use prefetch_related() to fetch all replies in one query
    - Total queries: approximately 3-4 (depending on depth)
    
    How it works:
    1. Get all root comments (parent=None) with their authors
    2. Prefetch all nested replies with their authors
    3. Build the tree in Python (already cached)
    
    For simple UI (max depth 3-4), we can also fetch all comments
    in one query and build tree in Python - equally efficient.
    
    Args:
        post: Post object to get comments for
    
    Returns:
        QuerySet of root Comment objects with prefetched replies
    """
    # Fetch all root-level comments with their authors and replies
    root_comments = Comment.objects.filter(
        post=post,
        parent=None
    ).select_related('author').prefetch_related(
        Prefetch(
            'replies',
            queryset=Comment.objects.select_related('author').prefetch_related(
                'replies__author',  # For one more level of nesting
            ).order_by('created_at')
        )
    ).order_by('created_at')
    
    return root_comments
