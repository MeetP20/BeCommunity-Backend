from django.urls import path
from . import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('sign-up/',views.Register.as_view(), name='sign-up'),
    path('get_user/',views.get_user,name="get-user"),
    path('get_community/',views.get_community,name='get_community'),
    path('join/',views.joinCommunity,name='join-community'),
    path('create-community/',views.createCommunity,name='create-community'),
    path('get-categories/',views.getCategories, name="get-categories"),
    path('create-post/', views.community_post, name="create-post"),
    path('get-post/',views.getPost, name="get-post"),
    path('get_user_joined_community/', views.get_user_joined_communities, name="get-user-joined-community"),
    path('edit_profile/',views.edit_profile,name="edit_profile"),
    path('get_user_profile/',views.get_edit_profile_data,name="get_user_profile"),
    path('get_one_community_info/<str:id>/',views.get_one_community_info, name="get_one_community"),
    path('make_comment/<str:post_id>/', views.makeComment, name="make_comment"),
    path('like_post/<str:post_id>/', views.likePost, name="like_post"),
    path('dislike_post/<str:post_id>/', views.dislikePost, name="dislike_post"),
    path('get_comments/<str:post_id>/',views.get_comments, name="get_comments"),
    path('make_reply/<str:post_id>/<str:comment_id>/',views.makeReply, name="make_reply"),
]

