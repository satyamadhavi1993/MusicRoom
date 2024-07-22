from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView, CustomLoginView, user_logout
from music_room import settings

app_name = "user"

urlpatterns = [
    path("", CustomLoginView.as_view(), name="login"),
    path("login/", CustomLoginView.as_view(), name="login"),
    # path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("logout/", user_logout, name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
]
