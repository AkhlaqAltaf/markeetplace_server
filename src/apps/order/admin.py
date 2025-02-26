from src.apps.order.models import Order, OrderItem
from src.apps.core.admin import admin_site

# Register your models here.
admin_site.register(Order)
admin_site.register(OrderItem)