from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class LeaderboardUserSerializer(serializers.ModelSerializer):
    """
    Serializer for leaderboard users.
    Shows username and karma earned in last 24 hours.
    """
    karma_24h = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'karma_24h', 'bio']
