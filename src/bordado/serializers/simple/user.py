from django.contrib.auth.models import User
from rest_framework import serializers


__all__ = [
    'UserSerializer',
]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
        ]
        read_only=True
