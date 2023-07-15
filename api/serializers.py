from rest_framework import serializers
from rest_framework.response import Response
from .models import User, Community, Category, Post
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

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "image"]

class GetCommunitySerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(source='creator.username', read_only=True)
    image = serializers.SerializerMethodField()
    membors = serializers.SerializerMethodField()
    def get_membors(self, instance):
        return instance.membors.count()

    def get_image(self, community):
        if community.image:
            # Encode image data to base64 string
            image_data = community.image.tobytes();
            image_data = base64.b64decode(image_data)
            image = base64.b64encode(image_data).decode('utf-8')
            return image
        return None
    class Meta:
        model = Community
        fields = ['id','name', 'description','creator', 'image', 'membors']


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
            image_data = validated_data.pop('image', None)
            if image_data:
                validated_data['image'] = base64.b64encode(image_data.read())
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
    image = serializers.SerializerMethodField()
    def get_image(self, post):
        if post.image:
            # Encode image data to base64 string
            image_data = post.image.tobytes()
            image_data = base64.b64decode(image_data)
            image = base64.b64encode(image_data).decode('utf-8')
            return image
        return None
    class Meta:
        model=Post
        fields = ['id','title', 'description', 'post_creator', 'community', 'image','likes','dislikes', 'date']


def validate_empty_string(value):
    if value == '':
        return None
    return value

class EditProfileSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model=User
        fields = ['id', 'bio', 'image', 'dob']

    def update(self,instance, validated_data):
        image_data = validated_data.pop('image', None)
        if image_data :
            instance.image = base64.b64encode(image_data.read())
        # user_id = validated_data.pop('user')
        # user = User.objects.get(id=user_id)
        instance.bio = validated_data['bio']
        # user.image = validated_data['image']
        instance.dob = validated_data['dob']
        instance.save()
        return instance

    
    # def up(self, validated_data):
    #     image_data = validated_data.pop('image', None)
    #     if image_data:
    #         validated_data['image'] = base64.b64encode(image_data.read())  
    #     user = validated_data.pop('user')
    #     edit_obj = EditProfile.objects.create(user=user, **validated_data)
    #     edit_obj.save()
    #     return edit_obj
    

class GetProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields = ['user', 'recoveryEmail', 'bio', 'image', 'dob']