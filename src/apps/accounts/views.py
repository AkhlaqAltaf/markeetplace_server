from django.shortcuts import redirect, render
from django.views import View

from src.apps.accounts.forms import CustomLoginForm, UserRegistrationForm
from django.contrib.auth import login

class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        form = CustomLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('core:home')

        return render(request, self.template_name, {'form': form})
  





class UserRegistrationView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('core:home')  # Redirect to the desired page after registration

        return render(request, self.template_name, {'form': form})
