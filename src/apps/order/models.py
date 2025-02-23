
from django.db import models

from src.apps.accounts.models import CustomUser
from src.apps.product.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready_to_ship', 'Ready to Ship'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # New status field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"