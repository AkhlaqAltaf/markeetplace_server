from django.urls import path

from src.apps.order import views

app_name = 'order'


urlpatterns = [
    path('order-detail/<int:id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('place_order/', views.PlaceOrderView.as_view(), name='place_order'),
    path('my-orders/', views.UserOrderListView.as_view(), name='user_order_list'),
    path('cancel-order/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel_order'),

]
