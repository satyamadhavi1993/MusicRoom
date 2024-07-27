from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
        

# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         country = models.CharField(max_length=100, blank=True, null=True)
#         fields = ["first_name", "last_name", "email"]