from rest_framework import serializers
from rest_framework.response import Response
from .models import User, Community, Category, Post
from rest_framework import status
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
    class Meta:
        model=Post
        fields = ['title', 'description', 'post_creator', 'community']