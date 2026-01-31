from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Comment
from core.serializers import CommentSerializer, CommentCreateSerializer
from core.services import toggle_like


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for comments.
    
    list: GET /api/comments/?post=<post_id> - List all comments for a post
    create: POST /api/comments/ - Create new comment (authenticated users only)
    like: POST /api/comments/:id/like/ - Toggle like on comment
    """
    queryset = Comment.objects.select_related('author', 'post').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        """
        Filter comments by post if post parameter is provided.
        Returns only root comments - replies are nested in serializer.
        """
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post')
        
        if post_id:
            # Only return root comments - replies will be nested
            queryset = queryset.filter(post_id=post_id, parent=None)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """
        Toggle like on a comment.
        
        Works the same as post likes but awards 1 karma instead of 5.
        """
        comment = self.get_object()
        
        # Use service layer for business logic
        is_liked, karma_change = toggle_like(request.user, comment)
        
        return Response({
            'is_liked': is_liked,
            'like_count': comment.like_count,
            'karma_change': karma_change,
        })
