

from django import forms
from .models import Vendor




class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name','id_card_number', 'address', 'mobile_number', 'cr_file']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
