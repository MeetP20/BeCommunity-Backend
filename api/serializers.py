from rest_framework import serializers
from rest_framework.response import Response
from .models import User, Community, Category, Post, EditProfile
from rest_framework import status
from django.core.files.base import ContentFile
import base64
class Login(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

class Signup(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username' ,'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email = validated_data['email'],
            username=validated_data['username'],
            name = validated_data['name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user

class GetCommunitySerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(source='creator.username', read_only=True)
    image = serializers.ImageField(required=False)
    class Meta:
        model = Community
        fields = ['id','name', 'description','creator', 'image']


class GetCategories(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class PostSerializer(serializers.ModelSerializer):
    # post_creator = serializers.PrimaryKeyRelatedField(source='post_creater.username', read_only=True)
    # community = serializers.PrimaryKeyRelatedField(source='community.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model=Post
        fields = ['title', 'description', 'post_creator', 'community', 'image']
    
    def create(self, validated_data):
        if validated_data.get('image') is not None:
            post = Post(
                title=validated_data['title'],
                description=validated_data['description'],
                post_creator=validated_data['post_creator'],
                community=validated_data['community'],
                image=validated_data['image']
            )
        else:
            post = Post(
                title=validated_data['title'],
                description=validated_data['description'],
                post_creator=validated_data['post_creator'],
                community=validated_data['community'],
            )
        post.save()
        return post

class GetPostSerializer(serializers.ModelSerializer):
    community = serializers.PrimaryKeyRelatedField(source="community.name", read_only=True)
    post_creator = serializers.PrimaryKeyRelatedField(source="post_creator.username", read_only=True)
    class Meta:
        model=Post
        fields = ['title', 'description', 'post_creator', 'community', 'image']


def validate_empty_string(value):
    if value == '':
        return None
    return value

class EditProfileSerializer(serializers.ModelSerializer):
    recoveryEmail = serializers.EmailField(required=False, allow_null=True)
    dob = serializers.DateField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model=EditProfile
        fields = ['user', 'recoveryEmail', 'bio', 'image', 'dob']
    
    def create(self, validated_data):
        image_data = validated_data.pop('image', None)
        if image_data:
            validated_data['image'] = base64.b64encode(image_data.read())  
            
        user = validated_data.pop('user')
        edit_obj = EditProfile.objects.create(user=user, **validated_data)
        edit_obj.save()
        return edit_obj
    