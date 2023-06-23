from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import Signup, GetCommunitySerializer, GetCategories, PostSerializer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, Community, Category, Post
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from datetime import date
import datetime
User = get_user_model()

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

@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def get_user(request):
    header = request.META.get('Authorization')
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id') 
    user = User.objects.get(id=user_id)
    return Response(user.username, status=status.HTTP_302_FOUND)


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def get_community(request):
    data = request.data['data']
    l = {}
    for i in data:
        c = Category.objects.get(name=i)
        temp = Community.objects.filter(category=c.id)
        object_list = []
        t = []
        for o in temp:
            t.append(o)
        serializer = GetCommunitySerializer(data=t, many=True)
        serializer.is_valid()
        serialized_data = serializer.data
        l[i] = serialized_data
        
    return Response(l)

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def joinCommunity(request):
    community_id = request.data['id']
    print(community_id)
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    community = Community.objects.get(id=community_id)
    print(community.membors.all())
    if community.membors.filter(id=user_id).exists():
        print("hello")
        return Response({'status':status.HTTP_403_FORBIDDEN})
    community.membors.add(user_id)
    community.save()
    print(community.membors.all())

    return Response({'status':status.HTTP_201_CREATED})


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def createCommunity(request):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    data = request.data
    name = data['name']
    description = data['description']
    creator = user_id
    category_list = data['category']
    image = data['image']
    user = User.objects.get(id=creator)
    community = Community.objects.create(name=name, description=description,creator=user,image=image)
    community.save()
    for category in category_list:
        current_category = Category.objects.get_or_create(name=category)
        community.category.add(current_category[0].id)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def getCategories(request):
    try:
        category_queryset = Category.objects.all()
        serializer = GetCategories(data=category_queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def community_post(request):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    data = request.data
    title = data['title']
    description = data['description']
    community_name = data['community_name']
    user = User.objects.get(id=user_id)
    community = Community.objects.get(name=community_name)
    context = {
        "title":title,
        "description":description,
        "post_creator":user.id,
        "community":community.id
    }
    serializer = PostSerializer(data=context)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def getPost(request):
    id=4
    communites_set = Community.objects.filter(membors=id)
    print(communites_set)
    new_post = []
    for i in communites_set:
        post = Post.objects.filter(community=i.id)
        post = post.filter(date__gte=datetime.date.today()).order_by('-creation_time')
        new_post.append(post)
    
    print(new_post)
    return Response(status=status.HTTP_200_OK)