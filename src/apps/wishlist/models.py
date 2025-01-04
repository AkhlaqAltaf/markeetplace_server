from django.db import models

from src.apps.accounts.models import CustomUser
from src.apps.product.models import Product


class WishListProduct(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wish_list')
    products = models.ManyToManyField(Product, related_name='wish_list', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} Wish List"

