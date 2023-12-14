from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("", include("django.contrib.auth.urls")),
    # user_registration and edditing
    path("register/", views.register, name="register"),
    path("edit/", views.edit, name="edit"),
    # user pages views
    path("users/", views.user_list, name="user_list"),
    path("roses_liked/", views.liked_roses, name="roses_liked"),
    path("photos_posted/", views.user_rose_pictures, name="photos_posted"),
    path("user_videos/", views.user_videos, name="user_videos"),
    path("articles_posted/", views.user_articles, name="articles_posted"),
    path("users/<username>", views.user_detail, name="user_detail"),
    path("users/follow/<str:user_id>", views.user_follow, name="user_follow"),
    path("users/unfollow/<str:user_id>", views.user_unfollow, name="user_unfollow"),
    path("delete_page/", views.delete_page, name="delete_page"),
    path("delete_account/", views.delete_account, name="delete_account"),
]
