from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from src.apps.vendor.forms import ProductForm
from src.apps.vendor.models import Vendor
from django.utils.text import slugify

from src.apps.accounts.models import CustomUser
from src.apps.vendor.models import Vendor
from src.apps.vendor.forms import ProductForm, VendorForm

# Converting Title into Slug
from django.utils.text import slugify

# Create your views here.


def vendors(request):
    return render(request, 'vendor/vendors.html')


class BecomeVendorView(View):
    template_name = 'vendor/become_vendor.html'

    def get(self, request):
        vendor_form = VendorForm()
        return render(request, self.template_name, {'form': vendor_form})

    def post(self, request):
        vendor_form = VendorForm(request.POST, request.FILES)

        if vendor_form.is_valid():
            # Create the user
            email = vendor_form.cleaned_data['email']
            password = request.POST.get('password')
            user_data = CustomUser.objects.create_user(email=email, password=password)

            if isinstance(user_data, dict):  # Check for status code in response
                if user_data['status_code'] == 600:
                    vendor_form.add_error('email', user_data['message'])
                    return render(request, self.template_name, {'form': vendor_form})

            user = user_data['user']

            # Create the vendor
            Vendor.objects.create(
                name=vendor_form.cleaned_data['name'],
                email=vendor_form.cleaned_data['email'],
                id_card_number=vendor_form.cleaned_data['id_card_number'],
                address=vendor_form.cleaned_data['address'],
                mobile_number=vendor_form.cleaned_data['mobile_number'],
                cr_file=vendor_form.cleaned_data['cr_file'],
                created_by=user,
            )

            login(request, user)
            return redirect('core:home')

        return render(request, self.template_name, {'form': vendor_form})


class CheckVendorMixin:
    """
    Mixin to check if the user is a vendor. Redirect to become-vendor if not.
    """
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'vendor'):
            return redirect('vendor:become-vendor')
        return super().dispatch(request, *args, **kwargs)


class VendorAdminView(LoginRequiredMixin, CheckVendorMixin, View):
    template_name = 'vendor/vendor_admin.html'

    def get(self, request, *args, **kwargs):
        vendor = request.user.vendor
        products = vendor.products.all()
        orders = vendor.orders.all()

        for order in orders:
            order.vendor_amount = 0
            order.vendor_paid_amount = 0
            order.fully_paid = True

            for item in order.items.all():
                if item.vendor == vendor:
                    if item.vendor_paid:
                        order.vendor_paid_amount += item.get_total_price()
                    else:
                        order.vendor_amount += item.get_total_price()
                        order.fully_paid = False

        return render(request, self.template_name, {'vendor': vendor, 'products': products, 'orders': orders})


class AddProductView(LoginRequiredMixin, CheckVendorMixin, View):
    template_name = 'vendor/add_product.html'

    def get(self, request, *args, **kwargs):
        form = ProductForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.slug = slugify(product.title)
            product.save()
            return redirect('vendor:vendor-admin')
        return render(request, self.template_name, {'form': form})


class EditVendorView(LoginRequiredMixin, CheckVendorMixin, View):
    template_name = 'vendor/edit_vendor.html'

    def get(self, request, *args, **kwargs):
        vendor = request.user.vendor
        return render(request, self.template_name, {'vendor': vendor})

    def post(self, request, *args, **kwargs):
        vendor = request.user.vendor
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')

        if name:
            vendor.created_by.email = email
            vendor.created_by.save()
            vendor.name = name
            vendor.save()
            return redirect('vendor:vendor-admin')

        return render(request, self.template_name, {'vendor': vendor})


class VendorsView(View):
    template_name = 'vendor/vendors.html'

    def get(self, request, *args, **kwargs):
        vendors = Vendor.objects.all()
        return render(request, self.template_name, {'vendors': vendors})


class VendorDetailView(View):
    template_name = 'vendor/vendor.html'

    def get(self, request, vendor_id, *args, **kwargs):
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        return render(request, self.template_name, {'vendor': vendor})
