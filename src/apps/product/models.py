import os

from src.apps.accounts.models import CustomUser
from src.apps.vendor.models import Vendor
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files import File
from ckeditor.fields import RichTextField


# PRODUCT PARENT CATEGORY


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



# PRODUCT COUNTRY ORIGIN

class CountryOrigin(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name



# PRODUCT MODEL


class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('review', 'Under Review'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='products')

    tags = models.ManyToManyField('Tag', blank=True)  # Tags are optional
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=10, default='USD')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='review')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    sales_count = models.PositiveIntegerField(default=0)
    country_of_origin = models.ManyToManyField(CountryOrigin, related_name='products')
    content = RichTextField()
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

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

# PRODUCT MEDIA

class Media(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="products/", default='https://via.placeholder.com/240x180.jpg')
    media_type = models.CharField(max_length=10, editable=False)  # Editable is False to set it programmatically.

    def make_thumbnail(self, image, size=(300, 200)):
        """
        Generate a thumbnail for the uploaded image.
        """
        img = Image.open(image)
        img = img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)
        return thumbnail

    def save(self, *args, **kwargs):
        """
        Override the save method to handle file type and thumbnail creation.
        """
        if self.file:
            # Extract the file extension
            ext = os.path.splitext(self.file.name)[1].lower()

            # Check the file type and act accordingly
            if ext in ['.jpg', '.jpeg', '.png']:
                # Set media_type as 'image'
                self.media_type = 'image'

                # Generate a thumbnail and replace the file
                self.file = self.make_thumbnail(self.file)
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                # Set media_type as 'video'
                self.media_type = 'video'
            else:
                raise ValueError(f"Unsupported file type: {ext}. Only images and videos are allowed.")

        super().save(*args, **kwargs)  # Call the original save method
#





# # Create your models here.

#
#
#
# class Product(models.Model):
#     vendor = models.ForeignKey(Vendor, related_name="products", on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     country_of_origin = models.CharField(max_length=100)
#     category = models.CharField(max_length=100)
#     sub_category = models.CharField(max_length=100)
#     summary = models.TextField()
#     description = models.TextField()
#
#     def __str__(self):
#         return self.name
#
#
#
# from PIL import Image
# from io import BytesIO
# from django.core.files import File
#
# class ProductMedia(models.Model):
#     product = models.ForeignKey(Product, related_name='media', on_delete=models.CASCADE)
#     media_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')])
#     file = models.FileField(upload_to='uploads/')
#     thumbnail = models.ImageField(upload_to='uploads/thumbnails/', blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.media_type} - {self.product.name}"
#
#     def save(self, *args, **kwargs):
#         if self.media_type == 'image' and not self.thumbnail:
#             self.thumbnail = self.make_thumbnail(self.file)
#         super().save(*args, **kwargs)
#
#     def make_thumbnail(self, image, size=(300, 200)):
#         img = Image.open(image)
#         img.convert('RGB')
#         img.thumbnail(size)
#
#         thumb_io = BytesIO()
#         img.save(thumb_io, 'JPEG', quality=85)
#
#         thumbnail = File(thumb_io, name=image.name)
#
#         return thumbnail
#
#
# class ShippingMethod(models.Model):
#     product = models.OneToOneField(Product, on_delete=models.CASCADE)
#     method = models.CharField(
#         max_length=50,
#         choices=[
#             ('Ex-Mill', 'Ex-Mill'),
#             ('FOB', 'FOB'),
#             ('CNF', 'CNF'),
#             ('CIF', 'CIF'),
#             ('As Per Request', 'As Per Request'),
#         ],
#     )
#     price_method = models.CharField(
#         max_length=50,
#         choices=[
#             ('Letter Of Credit', 'Letter Of Credit'),
#             ('Escrow', 'Escrow'),
#             ('Telegraphic Transfer', 'Telegraphic Transfer'),
#             ('Helgro Wallet', 'Helgro Wallet'),
#             ('Crypto', 'Crypto'),
#         ],
#     )
#
#     def __str__(self):
#         return f"Shipping: {self.method} | Pricing: {self.price_method} for {self.product.name}"
# class Document(models.Model):
#     product = models.ForeignKey(Product, related_name='documents', on_delete=models.CASCADE)
#     document_name = models.CharField(max_length=255)
#     file = models.FileField(upload_to='documents/')
#
#     def __str__(self):
#         return self.document_name
#

# class Product(models.Model):
#     category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
#     vendor = models.ForeignKey(Vendor, related_name="products", on_delete=models.CASCADE)
#     title = models.CharField(max_length=50)
#     slug = models.SlugField(max_length=55)
#     description = models.TextField(blank=True, null=True)
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     added_date = models.DateTimeField(auto_now_add=True)
#     image = models.ImageField(upload_to='uploads/', blank=True, null=True)
#     thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True) # Change uploads to thumbnails
#
#     class Meta:
#         ordering = ['-added_date']
#
#     def __str__(self):
#         return self.title
#
#
#     def get_thumbnail(self):
#         if self.thumbnail:
#             return self.thumbnail.url
#         else:
#             if self.image:
#                 self.thumbnail = self.make_thumbnail(self.image)
#                 self.save()
#                 return self.thumbnail.url
#
#             else:
#                 # Default Image
#                 return 'https://via.placeholder.com/240x180.jpg'
#
#     # Generating Thumbnail - Thumbnail is created when get_thumbnail is called
#     def make_thumbnail(self, image, size=(300, 200)):
#         img = Image.open(image)
#         img.convert('RGB')
#         img.thumbnail(size)
#
#         thumb_io = BytesIO()
#         img.save(thumb_io, 'JPEG', quality=85)
#
#         thumbnail = File(thumb_io, name=image.name)
#
#         return thumbnail
#

