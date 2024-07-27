from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import change_password, RegisterView, CustomLoginView, user_logout
from music_room import settings

app_name = "user"

urlpatterns = [
    # path("", CustomLoginView.as_view(), name="login"),
    path("change_password/", change_password, name="change_password"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", user_logout, name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
]
