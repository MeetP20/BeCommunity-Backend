from rest_framework import serializers

from .models import User

class Login(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']