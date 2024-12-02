from django.urls import path
from dj_rest_auth.views import LoginView
from .views import LoginView, UserRegistrationView

app_name = 'accounts'
urlpatterns = [
    path('login/',LoginView.as_view(),name="login"),
    path('register/', UserRegistrationView.as_view(), name='register'),

]
