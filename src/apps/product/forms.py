from django import forms

from src.apps.product.models import Category, CountryOrigin, Product, Media, SubCategory
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
        fields = ['name', 'currency', 'price', 'discount_price', 'sku', 'stock_quantity', 'category', 'sub_category', 'description', 'country_of_origin','product_image']

    # Additional field validations
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not Category.objects.filter(id=category.id).exists():
            raise forms.ValidationError("Invalid category.")
        return category

    def clean_sub_category(self):
        sub_category = self.cleaned_data.get('sub_category')
        category = self.cleaned_data.get('category')
        if sub_category and not SubCategory.objects.filter(id=sub_category.id, category=category).exists():
            raise forms.ValidationError("Invalid sub-category.")
        return sub_category

    def clean_country_of_origin(self):
        country = self.cleaned_data.get('country_of_origin')
        if not CountryOrigin.objects.filter(id=country.id).exists():
            raise forms.ValidationError("Invalid country of origin.")
        return country


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
