from django import forms

from src.apps.product.models import Category, Product, Media, SubCategory
from ckeditor.widgets import CKEditorWidget


# class AddToCartForm(forms.Form):
#     quantity = forms.IntegerField()

class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
class SubCategoryCreateForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'image', 'category']  # Include the category field here

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()  # Ensure we have a list of available categories

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['product','file']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'sub_category',
            'price',  'stock_quantity', 'sku',
             'brand'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': CKEditorWidget(attrs={'rows': 5}),  # Use CKEditorWidget for RichTextField
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sub_category': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'tags': 'Select multiple tags if applicable.',
            'country_of_origin': 'Select all applicable countries.',
        }


# Media Form (handling multiple files without ClearableFileInput)


# SubCategory Form (for inline creation)
class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Sub-category name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
