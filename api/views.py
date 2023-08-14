from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import Signup, GetCommunitySerializer, GetCategories, PostSerializer, GetPostSerializer, EditProfileSerializer, GetProfileSerializer, CommentSerializer, PostLikeSerializer, PostDislikeSerializer, GetCommentSerializer, ReplySerializer, CommentLikeSerializer, CommentDislikeSerilaizer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, Community, Category, Post, PostLikes, PostDislike, Comments, CommentLikes
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from datetime import date
from django.forms.models import model_to_dict
import base64
import datetime
from django.utils import timezone
import json
from datetime import timedelta
from django.core.serializers import serialize
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
@permission_classes([IsAuthenticatedOrReadOnly])
def get_user(request):
    header = request.META.get('Authorization')
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id') 

    user = User.objects.get(id=user_id)
    print(user.__dict__)
    user = user.__dict__

    image = user['image']
    image = image.tobytes()
    image_data = base64.b64decode(image)
    image_data = base64.b64encode(image_data).decode('utf-8')
    
    context = {
        "username":user["username"],
        "image":image_data
    }

    
    return Response(context)


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
    data = request.data['data']
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    for community_id in data:
        community = Community.objects.get(id=community_id)
        print(community.membors.all())
        if community.membors.filter(id=user_id).exists():
            return Response({'status':status.HTTP_403_FORBIDDEN})
        community.membors.add(user_id)
        community.save()

    return Response({'status':status.HTTP_201_CREATED})


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def createCommunity(request):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    data = request.data
    # user_id = data['creator']
    # data = json.loads(data)
    name = data['name']
    description = data['description']
    creator = user_id
    category_temp_list = data['community-category']
    # category_temp_list = request.POST.getlist('community-category')
    category_list = json.loads(category_temp_list)
    print(category_list)
    image = data['image-url']
    image_data = base64.b64encode(image.read())
    user = User.objects.get(id=creator)
    community = Community.objects.create(name=name, description=description,creator=user,image=image_data)
    community.save()
    community.membors.add(user_id)
    for category in category_list:
        current_category = Category.objects.get_or_create(name=category)
        print(current_category)
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
    community_name = data['community']
    if data.get('image-url') is not None:
        image = data['image-url']
    else:
        image = None
    print(image)
    user = User.objects.get(id=user_id)
    community = Community.objects.get(name=community_name)
    if image is not None:
        context = {
            "title":title,
            "description":description,
            "post_creator":user.id,
            "community":community.id,
            'image':image
        }
    else:
        context = {
            "title":title,
            "description":description,
            "post_creator":user.id,
            "community":community.id,
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
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    communites_set = Community.objects.filter(membors=user_id)
    print(communites_set)
    new_post = []
    one_hour_ago = timezone.now() - timedelta(hours=1200)
    for i in communites_set:
        post = Post.objects.filter(community=i.id)
        post = post.filter(date__gte=one_hour_ago).order_by('-date')
        new_post.extend(post)
        
    new_post.sort(key=lambda post:post.date, reverse=True)
    print(new_post)
    serializer = GetPostSerializer(new_post, many=True, context={"user_id":user_id})
    return Response(serializer.data,status=status.HTTP_200_OK)
    # if serializer.is_valid():
        
    # else:
    #     return Response(serializer.errors,status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def get_user_joined_communities(request):
    try:
        token = request.headers.get('Authorization').split()[1]
        decoded_token = RefreshToken(token)
        user_id = decoded_token.payload.get('id')
        community_set = Community.objects.filter(membors=user_id)
        serializer = GetCommunitySerializer(data=community_set, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_top_post(request):
    pass


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def edit_profile(request):
    data = request.data
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    data.update({'user':user_id})
    serializer = EditProfileSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get'])
@permission_classes([])
@authentication_classes([])
def get_edit_profile_data(request):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    profile_obj = User.objects.filter(id=user_id).first()
    serialized_profile = serialize('json', [profile_obj])
    profile_data = serialized_profile[1:-1]
    image_data = profile_obj.image.tobytes()
    image_data = base64.b64decode(image_data)
    image_encoded = base64.b64encode(image_data).decode('utf-8')

    context = {
        "user_id": profile_obj.id,
        "username":profile_obj.username,
        "dob": profile_obj.dob,
        "image": image_encoded,
        "bio": profile_obj.bio
    }
    return Response(context)

@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def get_one_community_info(request, id):
    community = Community.objects.get(id=id)
    post = Post.objects.filter(community=community.id)
    community_serializer = GetCommunitySerializer(community)
    serializer = GetPostSerializer(post, many=True)    
    context = {
        "community":community_serializer.data,
        "posts": serializer.data,
    }
    return Response(context, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def makeComment(request, post_id):
    data = request.data
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    data.update({"post":post_id, "author":user_id})
    serializer = CommentSerializer(data = data)
    if serializer.is_valid():
        serializer.save()
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([])
def likePost(request, post_id):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    serializer = PostLikeSerializer(data={"post":post_id, "user":user_id})
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([])
def dislikePost(request, post_id):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    if PostLikes.objects.filter(post=post_id, user=user_id).exists():
        like = PostLikes.objects.get(post=post_id, user=user_id)
        like.delete()
    serializer = PostDislikeSerializer(data={"post":post_id, "user":user_id})
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([])
def get_comments(request, post_id):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    comments = Comments.objects.filter(post=post_id, parent=None)
    serializer = GetCommentSerializer(comments, many=True, context={"user_id":user_id})
    # serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def makeReply(request, post_id, comment_id):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    data = request.data
    data.update({'post':post_id,'author':user_id,'parent':comment_id})
    serializer = ReplySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([])
def get_one_post(request, post_id):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    post = Post.objects.get(id=post_id)
    serializer = GetPostSerializer(post, context={"user_id":user_id})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def likeComments(request, comment_id):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    serializer = CommentLikeSerializer(data={'comment':comment_id, 'user':user_id})
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([])
def dislikeComment(request, comment_id):
    token = request.headers.get('Authorization').split()[1]
    decoded_token = RefreshToken(token)
    user_id = decoded_token.payload.get('id')
    if CommentLikes.objects.filter(comment=comment_id, user=user_id).exists():
        like = CommentLikes.objects.get(comment=comment_id, user=user_id)
        like.delete()
    serializer = CommentDislikeSerilaizer(data={'comment':comment_id, 'user':user_id})
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)