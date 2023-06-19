from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# Create your models here.

class UserManager(BaseUserManager):
    def create_superuser(self, email, username,name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, username,name, password, **other_fields)

    def create_user(self, email, username, name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username,name=name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=254,unique=True)
    username = models.CharField(max_length=54, unique=True)
    name = models.CharField(max_length=54)
    is_staff = models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','name']


class Category(models.Model):
    name = models.CharField(max_length=50,blank=False,null=False)

    def __str__(self):
        return self.name

class Community(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.CharField(max_length=254, blank=True, null=True)
    image = models.ImageField(upload_to='community', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE,related_name='creator')
    membors = models.ManyToManyField(User, blank=True)
    category = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=254, blank=False, null=False)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="Post", blank=True)
    likes = models.BigIntegerField(default=0)
    post_creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="post_creator")
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="community")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

