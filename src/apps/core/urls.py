from django.urls import path
from . import views
app_name = 'core'
urlpatterns = [
    path('', views.LandingPageView.as_view(), name="home"),
    path('contact-us/', views.ContactUsView.as_view(), name="contact"),
    path('about-us/', views.AboutUsView.as_view(), name="about"),
]