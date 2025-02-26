from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.cart_detail, name="cart"),
    path('addToCart/<int:id>/<int:quantity>/', views.AddToCartView.as_view(), name='addToCart'),
    path('add_with_offer/<int:id>/<int:quantity>/<int:offerid>/', views.AddToCartWithOffer.as_view(), name='add_with_offer'),
]
