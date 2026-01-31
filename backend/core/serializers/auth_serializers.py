from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates passwords match and creates new user account.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'bio']
        extra_kwargs = {
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        """Ensure passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match"
            })
        return attrs
    
    def create(self, validated_data):
        """Create new user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Returns username and password for JWT token generation.
    """
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data.
    Includes karma calculation fields.
    """
    total_karma = serializers.IntegerField(read_only=True)
    karma_24h = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'bio',
            'created_at',
            'total_karma',
            'karma_24h',
        ]
        read_only_fields = ['id', 'created_at', 'total_karma']
    
    def get_karma_24h(self, obj):
        """Calculate karma from last 24 hours"""
        return obj.karma_last_24h()
