from django.contrib.auth import login

from django.shortcuts import render, redirect

from django.urls import reverse_lazy

from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterForm

class RegisterView(LoginRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = "user/register.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("booking:calendar")
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("booking:calendar")
        return super().get(*args, **kwargs)
