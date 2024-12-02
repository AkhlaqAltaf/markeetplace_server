from django.forms import ModelForm, models

from src.apps.product.models import Product

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Vendor

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'image', 'title', 'description', 'price']




class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'email', 'id_card_number', 'address', 'mobile_number', 'cr_file']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
