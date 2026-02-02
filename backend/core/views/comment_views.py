from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Comment
from core.serializers import CommentSerializer, CommentCreateSerializer
from core.services import toggle_like


class CommentViewSet(viewsets.ModelViewSet):
    # Comments on posts - handles creating, viewing, and liking
    queryset = Comment.objects.select_related('author', 'post').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        # Simpler serializer for creating comments
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        # Filter by post ID if provided - only return root level comments
        # The replies get nested inside via  the serializer
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post')
        
        if post_id:
            # Only return root comments - replies will be nested
            queryset = queryset.filter(post_id=post_id, parent=None)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        # Same as liking posts, but comments give less karma (1 instead of 5)
        comment = self.get_object()
        
        # toggle_like handles the atomic transaction stuff
        is_liked, karma_change = toggle_like(request.user, comment)
        
        return Response({
            'is_liked': is_liked,
            'like_count': comment.like_count,
            'karma_change': karma_change,
        })
