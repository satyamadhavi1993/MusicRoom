from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView
from music_room import settings

app_name = "user"

urlpatterns = [
    path("", LoginView.as_view(template_name='user/login.html'), name="login"),
    path("login/", LoginView.as_view(template_name='user/login.html'), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
]
