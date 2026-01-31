from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Post
from core.serializers import PostSerializer, PostCreateSerializer
from core.services import toggle_like


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoints for posts.
    
    list: GET /api/posts/ - List all posts (paginated)
    create: POST /api/posts/ - Create new post (authenticated users only)
    retrieve: GET /api/posts/:id/ - Get single post
    like: POST /api/posts/:id/like/ - Toggle like on post
    """
    queryset = Post.objects.select_related('author').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """
        Toggle like on a post.
        
        This endpoint demonstrates the race condition solution:
        - Uses atomic transaction in toggle_like service
        - Database constraint prevents double-likes
        - Returns new like status and karma change
        """
        post = self.get_object()
        
        # Use service layer for business logic
        is_liked, karma_change = toggle_like(request.user, post)
        
        return Response({
            'is_liked': is_liked,
            'like_count': post.like_count,
            'karma_change': karma_change,
        })
