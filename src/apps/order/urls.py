from django.urls import path

from src.apps.order import views

app_name = 'order'


urlpatterns = [
    path('order-detail/<int:id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('place_order/', views.PlaceOrderView.as_view(), name='place_order'),
    path('my-orders/', views.UserOrderListView.as_view(), name='user_order_list'),
    path('cancel-order/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel_order'),


    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('orders/filter/<str:status>/',views.OrderFilterView.as_view(), name='order_filter'),
    path('orders/update/<int:order_id>/',views.UpdateOrderStatusView.as_view(), name='update_order_status'),

]
