from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Post
from core.serializers import PostSerializer, PostCreateSerializer
from core.services import toggle_like


class PostViewSet(viewsets.ModelViewSet):
    # Handles posts - viewing, creating, liking
    queryset = Post.objects.select_related('author').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        # Use simpler serializer for creating posts (don't need all the related data)
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        # Like/unlike a post - toggle_like handles the race condition stuff
        post = self.get_object()
        
        # toggle_like does the actual liking with atomic transaction
        is_liked, karma_change = toggle_like(request.user, post)
        
        return Response({
            'is_liked': is_liked,
            'like_count': post.like_count,
            'karma_change': karma_change,
        })
