from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    

    class Meta:
        model = User
        fields = ['username']

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        ]


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']

        def validate(self, data):
            if data['username'] == 'me':
                raise serializers.ValidationError(
                    'Username unavailable'
                )
            return data