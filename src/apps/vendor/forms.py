from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django import forms
from .models import Vendor
from ..product.models import ProductOffer, OrderOffer, Product, SubCategory


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name','id_card_number', 'address', 'mobile_number', 'cr_file']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, Field
from crispy_forms.bootstrap import PrependedText, FormActions

class ProductOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        vendor = kwargs.pop('vendor', None)
        super().__init__(*args, **kwargs)
        if vendor:
            self.fields['products'].queryset = Product.objects.filter(vendor=vendor)


        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('discount_type', css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                Column('discount_value', css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                css_class='row'
            ),

            Row(
                Column('start_date', css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                Column('end_date', css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                css_class='row'
            ),
            Submit('submit', 'Save Offer', css_class='btn btn-primary w-100'),
        )

    class Meta:
        model = ProductOffer
        fields = ['discount_type', 'discount_value', 'products','start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class OrderOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        vendor = kwargs.pop('vendor', None)
        super().__init__(*args, **kwargs)
        if vendor:
            self.fields['products'].queryset = Product.objects.filter(vendor=vendor)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'  # Optional: Add Bootstrap styling
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.layout = Layout(
            Row(
                Column(Field('discount_type', css_class='form-control'), css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                Column(Field('discount_value', css_class='form-control'), css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                css_class='form-row'
            ),
            Field('min_products', css_class='form-control'),
            Row(
                Column(Field('start_date', css_class='form-control'), css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                Column(Field('end_date', css_class='form-control'), css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                css_class='form-row'
            ),
            Row(
                Column(Field('products', css_class='form-control'), css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                Column(Field('categories', css_class='form-control'), css_class='col-12 col-md-6'),  # Full-width on mobile, half on larger screens
                css_class='form-row'
            ),

        )

    class Meta:
        model = OrderOffer
        fields = ['discount_type', 'discount_value', 'min_products', 'start_date', 'end_date', 'products']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
