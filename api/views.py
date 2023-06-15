from django.shortcuts import render

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import Signup
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['id'] = user.id
        # ...
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class Register(APIView):
    permission_classes = (AllowAny, )
    def post(self, request):
        print(request.data)
        username = request.data['username']
        email = request.data['email']
        if User.objects.filter(username=username).exists():
            return Response(status=status.HTTP_409_CONFLICT)
        
        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_409_CONFLICT)

        serializer = Signup(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)