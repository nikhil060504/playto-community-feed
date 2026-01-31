from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.serializers import UserRegistrationSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/auth/register/
    
    Accepts: username, email, password, password_confirm, bio (optional)
    Returns: User data with JWT tokens
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create user and return user data"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return user data
        user_serializer = UserSerializer(user)
        return Response(
            user_serializer.data,
            status=status.HTTP_201_CREATED
        )


class CurrentUserView(APIView):
    """
    API endpoint to get current authenticated user.
    GET /api/auth/me/
    
    Returns: Current user's profile data with karma
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return current user data"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
