from django.contrib.auth import login, logout

from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterForm
from django.urls import reverse

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
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


class CustomLoginView(LoginView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("booking:calendar")
        return super().get(*args, **kwargs)
    
    
@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('login'))
    return render(request, 'registration/logout.html')
