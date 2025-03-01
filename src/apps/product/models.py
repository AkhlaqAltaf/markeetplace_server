import os
import uuid

from django.db.models import Sum

from src.apps.accounts.models import CustomUser
from src.apps.order.models import OrderItem
from src.apps.vendor.models import Vendor
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files import File
from ckeditor.fields import RichTextField
from src.apps.wishlist.models import WishListProduct




class Category(models.Model):
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    name = models.CharField(max_length=50)
    ordering = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return self.name


# PRODUCT SUB CATEGORY


class SubCategory(models.Model):
    image = models.ImageField(upload_to='sub_categories/', blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Brand(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='brands', blank=True)
    sub_categories = models.ManyToManyField(SubCategory, related_name='brands', blank=True)

    def __str__(self):
        return self.name
    def get_len_products(self):
        return self.products.count()

class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('review', 'Under Review'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, related_name='products')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='review')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    sales_count = models.PositiveIntegerField(default=0)
    content = RichTextField(blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.status = 'inactive'
        self.save()
    def is_in_wishlist(self, user):
        """
        Check if the product is in the user's wishlist.

        :param user: CustomUser  instance
        :return: True if the product is in the user's wishlist, False otherwise
        """
        try:
            wishlist = WishListProduct.objects.get(user=user)
            return self in wishlist.products.all()
        except WishListProduct.DoesNotExist:
            return False

    def get_total_price(self, quantity, offer_id=None):
        """
        Calculate the total price based on quantity and optional offer.

        :param quantity: The quantity of the product
        :param offer_id: The ID of the offer to apply (if any)
        :return: The total price
        """
        total_price = self.price * quantity  # Default total price without offer

        if offer_id:
            try:
                offer = Offer.objects.get(id=offer_id, product=self)
                # Calculate discounted price
                discounted_price_per_unit = self.price * (1 - offer.discount_percentage / 100)
                total_price = discounted_price_per_unit * quantity
            except Offer.DoesNotExist:
                pass  # If the offer does not exist, use the default price

        return round(total_price, 2)  # Return total price rounded to 2 decimal places

    def get_total_sales(self):
        """
        Calculate the total quantity of sold products.

        :return: Total quantity sold
        """
        total_sold = OrderItem.objects.filter(product=self).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return total_sold

class Offer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    min_quantity = models.PositiveIntegerField()
    max_quantity = models.PositiveIntegerField(null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    def calculate_discounted_price(self):
        """Calculate total price after discount"""
        if self.min_quantity < self.min_quantity or (self.max_quantity and self.min_quantity > self.max_quantity):
            return None  # Not eligible for discount
        discounted_price_per_unit = self.product.price * (1 - self.discount_percentage / 100)
        total_price = discounted_price_per_unit * self.min_quantity
        return round(total_price,2)

    def calculate_average_price(self):
        """Calculate average price per unit after discount"""
        total_price = self.calculate_discounted_price()
        if total_price is None:
            return None
        return  round(total_price / self.min_quantity,2)

    def __str__(self):
        return f"{self.product.name} - {self.discount_percentage}% off on {self.min_quantity}+"


# Product Tag Model

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# PRODUCT VARIENTS

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Variant of {self.product.name}"

# PRODUCT SHIPMENT ADDRESS

class ShippingInfo(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='shipping_info')
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text='Weight in kilograms')
    dimensions = models.CharField(max_length=100, help_text='Format: Length x Width x Height in cm', blank=True, null=True)
    shipping_class = models.CharField(max_length=50, blank=True, null=True)
    availability = models.TextField(help_text='List of regions or countries', blank=True, null=True)

    def __str__(self):
        return f"Shipping Info for {self.product.name}"


# Product Review Model
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(help_text="Rating out of 5")
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.name}"

class Media(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="products/", default='https://via.placeholder.com/240x180.jpg')
    media_type = models.CharField(max_length=10, editable=False)
    is_primary = models.BooleanField(default=False)

    def make_thumbnail(self, image, size=(536, 536)):
        """
        Generate a thumbnail for the uploaded image.
        """
        if self.is_primary:
            return image

        return image

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure unique filenames and handle file type detection.
        """
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()

            # Generate a unique filename
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            self.file.name = os.path.join("products/", unique_filename)

            # Set media type based on file extension
            if ext in ['.jpg', '.jpeg', '.png']:
                self.media_type = 'image'
                self.file = self.make_thumbnail(self.file)  # Generate a thumbnail
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                self.media_type = 'video'
            elif ext in ['.glb', '.gltf', '.obj', '.fbx']:
                self.media_type = '3d'
            else:
                raise ValueError(f"Unsupported file type: {ext}. Only images, videos, and 3D models are allowed.")

        super().save(*args, **kwargs)

class TopPageProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='top_page')
    order = models.PositiveSmallIntegerField(default=0)
    def __str__(self):
        return f"{self.product.name}"



class LandingPageProduct(models.Model):
    slide1_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='slide1', null=True, blank=True)
    slide2_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='slide2', null=True, blank=True)
    slide3_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='slide3', null=True, blank=True)
    exc1_offer_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='exc1_offer', null=True, blank=True)
    exc2_offer_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='exc2_offer', null=True, blank=True)
    exc3_offer_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='exc3_offer', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Ensure only one instance of LandingPageProduct exists
        if not self.pk and LandingPageProduct.objects.exists():
            raise ValueError("There can only be one LandingPageProduct instance.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Landing Page Products"

class ProductOffer(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='product_offers')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product, blank=True, related_name='product_offers')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"Offer by {self.vendor.name} - {self.discount_value} {self.discount_type}"

class OrderOffer(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('fixed', 'Fixed')))
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_products = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"Order Offer by {self.vendor.name}"


