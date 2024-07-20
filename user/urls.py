from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView, user_logout
from music_room import settings

app_name = "user"

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", user_logout, name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
]
