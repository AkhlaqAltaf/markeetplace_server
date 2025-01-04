from django.urls import path

from src.apps.wishlist import views

app_name = 'wishlist'


urlpatterns =[
    path('wish_list/', views.WishListProductsView.as_view(), name='wish-list'),
    path('wishListCreate/<int:id>/', views.WishListProductsCreateView.as_view(), name='wish-list-create'),
    path('remove-from-wishlist/<int:product_id>/', views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),

]