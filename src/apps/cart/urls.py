from django.urls import path
from . import views



app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name="cart"),
    path('addToCart/<int:id>/<int:quantity>/', views.AddToCartView.as_view(), name='addToCart'),
]
