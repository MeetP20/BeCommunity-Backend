from rest_framework import serializers
from rest_framework.response import Response
from .models import User, Community, Category, Post, Comments, PostLikes, PostDislike, CommentDislike, CommentLikes
from rest_framework import status
from django.core.files.base import ContentFile
# from django.contrib.auth.models import User
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
    image = serializers.SerializerMethodField()
    membors = serializers.SerializerMethodField()
    def get_membors(self, instance):
        return instance.membors.count()

    def get_image(self, community):
        if community.image:
            # Encode image data to base64 string
            image_data = community.image.tobytes()
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
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    has_disliked = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        try:
            like = PostLikes.objects.filter(post=obj)
            return like.count()
        except PostLikes.DoesNotExist:
            return 0
    
    def get_has_liked(self, obj):
        user_id = self.context.get("user_id")
        print(user_id)
        return PostLikes.objects.filter(post=obj.__dict__["id"], user=user_id).exists()
             
    
    def get_dislikes_count(self, obj):
        try:
            dislike = PostDislike.objects.filter(post=obj)
            return dislike.count()
        except PostDislike.DoesNotExist:
            return 0
    
    def get_has_disliked(self, obj):
        user_id = self.context.get("user_id")
        try:
            dislike = PostDislike.objects.get(post=obj, user=user_id)
            return True
        except:
            return False

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
        fields = ['id','title', 'description', 'post_creator', 'community', 'image','likes_count','dislikes_count','has_liked','has_disliked', 'date',]


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


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ["post", "content","author"]
    
    def create(self, validated_data):
        comment = Comments.objects.create(**validated_data)
        comment.save()
        return comment

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLikes
        fields = ["post", "user"]

class PostDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostDislike
        fields = ["post", "user"]

class GetCommentSerializer(serializers.ModelSerializer):
    # post = serializers.PrimaryKeyRelatedField(source="post.id", read_only=True)
    author = serializers.PrimaryKeyRelatedField(source="author.username", read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    has_disliked = serializers.SerializerMethodField()
    reply_counts = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        try:
            like = CommentLikes.objects.filter(comment=obj)
            return like.count()
        except CommentLikes.DoesNotExist:
            return 0

    def get_dislikes_count(self, obj):
        try:
            dislike = CommentDislike.objects.filter(comment=obj)
            return dislike.count()
        except CommentDislike.DoesNotExist:
            return 0

    def get_has_liked(self, obj):
        user_id = self.context.get("user_id")
        
        try:
            like = CommentLikes.objects.get(comment=obj, user=user_id)
            return True
        except:
            return False
    
    def get_has_disliked(self, obj):
        user_id = self.context.get("user_id")
        try:
            dislike = CommentDislike.objects.get(comment=obj, user=user_id)
            return True
        except:
            return False
    
    def get_reply_counts(self, obj):
        try:
            reply = Comments.objects.filter(parent=obj)
            return reply.count()
        except:
            return 0

    def get_replies(self, obj):
        try:
            replies = Comments.objects.filter(parent=obj)
            serializer = GetCommentSerializer(replies, many=True)
            return serializer.data
        except:
            return []

    class Meta:
        model = Comments
        fields = ["id","post", "content", "author", "date", "parent", "likes_count", "dislikes_count", "has_liked", "has_disliked", "reply_counts", "replies"]

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ["post", "author", "content", "parent"]

    def create(self, validated_data):
        comment = Comments.objects.create(**validated_data)
        comment.save()
        return comment
        
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLikes
        fields = ["comment", "user"]

class CommentDislikeSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = CommentDislike
        fields = ["comment", "user"]

class GetAllCommunitySerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    def get_members(self, instance):
        return instance.membors.count()
    def get_image(self, instance):
        if instance.image:
            # Encode image data to base64 string
            image_data = instance.image.tobytes()
            image_data = base64.b64decode(image_data)
            image = base64.b64encode(image_data).decode('utf-8')
            return image
        return None
    class Meta:
        model = Community
        fields = ["id", "name", "members", "image"]