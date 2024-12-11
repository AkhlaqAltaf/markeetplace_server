from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# Converting Title into Slug
from django.utils.text import slugify
from django.views import View
from django.views.generic import CreateView

from src.apps.product.models import Category, CountryOrigin, Product, SubCategory, Tag, Media
from src.apps.vendor.forms import  VendorForm
from src.apps.vendor.models import Vendor


# Create your views here.


def vendors(request):
    return render(request, 'vendor/vendors.html')


class BecomeVendorView(View):
    template_name = 'vendor/become_vendor.html'

    def get(self, request):
        if request.user.is_authenticated:
            vendor_form = VendorForm()
            return render(request, self.template_name, {'form': vendor_form})
        else:
            return redirect('accounts:login')

    def post(self, request):
        vendor_form = VendorForm(request.POST, request.FILES)

        if vendor_form.is_valid():
            user = request.user
            Vendor.objects.create(
                name=vendor_form.cleaned_data['name'],
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


class CreateProduct(CreateView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        origins = CountryOrigin.objects.all()

        return render(request, template_name="vendor/add_product/addproduct.html", context={"categories": categories, 'origins': origins})

    def post(self, request, *args, **kwargs):
        global tag_objs, tag_names, origin_obj
        data = request.POST
        files = request.FILES  # Access files from the form submission

        category_name = data.get("category")
        category_obj = Category.objects.filter(name=category_name).first()
        sub_category_obj = SubCategory.objects.filter(name=data.get("sub_category"), category=category_obj).first()

        # Validation Errors Dictionary
        errors = {}

        # Required fields
        required_fields = ['name', 'price', 'stock_quantity', 'category', 'sub_category', 'description']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

        # Validate price
        price = data.get('price')
        if price:
            try:
                price = float(price)
                if price <= 0:
                    errors['price'] = "Price must be greater than 0."
            except ValueError:
                errors['price'] = "Price must be a valid number."

        sku = data.get('sku')
        if Product.objects.filter(sku=sku).exists():
            errors['sku'] = "This SKU is already in use. Please choose a unique SKU."

        # Validate stock_quantity
        stock_quantity = data.get('stock_quantity')
        if stock_quantity:
            try:
                stock_quantity = int(stock_quantity)
                if stock_quantity < 0:
                    errors['stock_quantity'] = "Stock quantity must be 0 or more."
            except ValueError:
                errors['stock_quantity'] = "Stock quantity must be an integer."

        # Validate category
        if not Category.objects.filter(name=category_name).exists():
            errors['category'] = "Invalid category selected."

        # Validate sub_category
        sub_category_name = data.get('sub_category')
        if not SubCategory.objects.filter(name=sub_category_name, category=category_obj).exists():
            errors['sub_category'] = "Invalid subcategory selected for the chosen category."

        # Check if there are validation errors
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # If data is valid, proceed with database insertion
        vendor = Vendor.objects.all().first()
        product = Product.objects.create(
            name=data.get("name"),
            description=data.get("description"),
            category=category_obj,
            sub_category=sub_category_obj,
            price=price,
            discount_price=data.get("discount_price"),
            stock_quantity=stock_quantity,
            sku=data.get("sku"),
            currency=data.get("currency"),
            content=data.get("content"),
            vendor=vendor
        )

        # Handling the uploaded images
        print("IMAGES",request.POST.get("images"))
        for file in files.getlist('images'):  # 'images' is the name of the file input field
            media = Media.objects.create(product=product, file=file)

        # Handling tags
        if data.get("tags"):
            tag_string = data.get("tags")
            tag_objs = []
            tag_names = tag_string.split(",")
            for tag_name in tag_names:
                tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                tag_objs.append(tag_obj)
            product.tags.set(tag_objs)

        # Handling the country of origin
        if data.get("country_of_origin"):
            origin_name = data.get("country_of_origin")
            origin_obj = CountryOrigin.objects.filter(name=origin_name).first()
            if origin_obj:
                product.country_of_origin.set([origin_obj])

        # Return success message
        return JsonResponse({'success': True, 'message': 'Product created successfully!'})

class GetSubCategory(View):
    def get(self, request, category):
        category_obj = Category.objects.filter(name=category).first()
        if not category_obj:
            return JsonResponse({"error": "Category not found"}, status=404)

        sub_categories = SubCategory.objects.filter(category=category_obj)
        # Simplify the response to include only id and name
        data = [{"id": sub.pk, "name": sub.name} for sub in sub_categories]

        return JsonResponse({"subcategories": data})
def addProductTest(request):
    return render(request,template_name="vendor/add_product/addproduct.html")


def home(request):
    return render(request, 'vendor/main/base.html')
def storeAnalytics(request):
    return render(request, 'vendor/storeanalytics.html')
def Account(request):
    return render(request, 'vendor/Account/base.html')
def General(request):
    return render(request, 'vendor/Account/General.html')
def Billing(request):
    return render(request, 'vendor/Account/Billing.html')
def Team(request):
    return render(request, 'vendor/Account/Team.html')
def Notification(request):
    return render(request, 'vendor/Account/Notifications.html')
def Secuirity(request):
    return render(request, 'vendor/Account/Secuirity.html')
def CustomerList(request):
    return render(request, 'vendor/customers/customerlist.html')
def CustomerDetails(request):
    return render(request, 'vendor/customers/customerdetail.html')