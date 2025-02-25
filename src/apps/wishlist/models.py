from django.db import models

from src.apps.accounts.models import CustomUser


class WishListProduct(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wish_list')
    products = models.ManyToManyField('product.Product', related_name='wish_list', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} Wish List"

