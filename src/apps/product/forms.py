from django import forms
from src.apps.product.models import Category, Product, Media, SubCategory
from ckeditor.widgets import CKEditorWidget

class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
class SubCategoryCreateForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'image', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()

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
             'brand','barcode','content'
        ]

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'category', 'image']

