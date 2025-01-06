import json
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
# Converting Title into Slug
from django.utils.text import slugify
from django.views import View
from django.views.generic import CreateView
from datetime import datetime
from src.apps.product.forms import ProductForm
from src.apps.product.models import Category, CountryOrigin, SubCategory, Tag, Media, Product
from src.apps.vendor.forms import VendorForm
from src.apps.vendor.models import Vendor
from .mixins import CheckVendorMixin
import base64
from django.core.files.base import ContentFile

from ..order.models import Order


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
            return redirect('/accounts')

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


class VendorSiteView(CheckVendorMixin,View):
    template_name = 'vendor/Analytics.html'
    def get(self,request):
        return  render(request, self.template_name)


class VendorAdminView(CheckVendorMixin, View):
    """This VIEW is For Vendor Admin Side"""
    template_name = 'vendor/Analytics.html'
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




class EditVendorView(CheckVendorMixin, View):
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
    
    
    

class AddProductView(CreateView):
    
    def get(self,request):     
        form = ProductForm()
        categories = Category.objects.all()
        origins = CountryOrigin.objects.all()
        return render(request, 'vendor/add_product/addproduct.html', context={"categories": categories, 'origins': origins,'form': form})
    def post(self,request):
        form = ProductForm(request.POST)
        print(request.POST.get('sub_category'))
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            images_data = request.POST.getlist('images')
# Check if the list is not empty and parse it
            if images_data:
                images_data = json.loads(images_data[0])  # Parse the first item in the list
            else:
                images_data = []            
            for image in images_data:
                file = self.convert_base64_image(image)
                if file:         
                   media = Media.objects.create(product=product, file=file)
                   
            print("VALIDATED FORM")
            return redirect('vendor:add')  # Or the appropriate page

        else:
            print("AGAIN PASS FORM ..",form.errors)
            categories = Category.objects.all()
            origins = CountryOrigin.objects.all()
            return render(request, 'vendor/add_product/addproduct.html', context={"categories": categories, 'origins': origins,'form': form})

    def convert_base64_image(self,base64_data):
        data = next(iter(base64_data.values()))
        if data.startswith("data:image"):
            data = data.split(",")[1]  
        # Decode the base64 string into binary data
        file_data = base64.b64decode(data)
        file_name = datetime.now()
        content_file = ContentFile(file_data,name=f"{file_name}.jpg")
        print(content_file)
        return content_file


class AddBulkProductsView(View):
    def get(self, request):
        categories = Category.objects.all()
        origins = CountryOrigin.objects.all()
        return render(request, 'vendor/add_product/add_bulk_products.html', context={"categories": categories, 'origins': origins})

    def post(self, request):
        try:
            data = json.loads(request.body)  # Parse the JSON data sent from the frontend
            products = data.get("products", [])  # Extract the list of products

            for product_data in products:
                print(products)
                # Populate the form with product data
                form = ProductForm(product_data)
                print(form.errors.items())
                if form.is_valid():
                    product = form.save(commit=False)
                    product.vendor = request.user.vendor
                    product.save()

                    # Handle images (if provided)
                    images_data = product_data.get("images", [])
                    for image in images_data:
                        file = self.convert_base64_image(image)
                        if file:
                            Media.objects.create(product=product, file=file)
                else:
                    return JsonResponse({"error": f"Invalid product data: {form.errors}"}, status=400)

            return JsonResponse({"message": "Products uploaded successfully!"}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Something went wrong: {str(e)}"}, status=500)

    def convert_base64_image(self, base64_data):
        try:
            if base64_data.startswith("data:image"):
                base64_data = base64_data.split(",")[1]
            # Decode the base64 string into binary data
            file_data = base64.b64decode(base64_data)
            file_name = datetime.now().strftime("%Y%m%d%H%M%S")
            content_file = ContentFile(file_data, name=f"{file_name}.jpg")
            return content_file
        except Exception as e:
            print(f"Error converting base64 image: {str(e)}")
            return None












class GetSubCategory(View):
    def get(self, request, category):
        category_obj = Category.objects.filter(id=category).first()
        if not category_obj:
            return JsonResponse({"error": "Category not found"}, status=404)
        sub_categories = SubCategory.objects.filter(category=category_obj)
        # Simplify the response to include only id and name
        data = [{"id": sub.pk, "name": sub.name} for sub in sub_categories]
        return JsonResponse({"subcategories": data})





def Register(request):
    return render(request, 'vendor/registration/registration2.html')



def storeAnalytics(request):
    return render(request, 'vendor/Analytics.html')

def InvoiceList(request):
    return render(request, 'vendor/invoice/invoicelist.html')
def InvoiceDetails(request):
    return render(request, 'vendor/invoice/invoicedetail.html')
def Calender(request):
    return render(request, 'vendor/calendar.html')
def ProductAdd(request):
    return render(request, 'vendor/products/createproduct.html')
def ProductList(request):
    return render(request, 'vendor/products/productlist.html')
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







class VendorProductListView(View):
    def get(self, request):
        # Get products associated with the current vendor
        products = Product.objects.filter(vendor=request.user.vendor)
        print("PRODUCTS",products)
        return render(request, 'vendor/products/productlist.html', {'products': products})




























# CREATING 3d MODEL


























import requests
import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import ThreeDModel


def list_models(request):
    models = ThreeDModel.objects.all()
    return render(request, 'vendor/3d/list_models.html', {'models': models})

def create_model(request):
    if request.method == 'POST':
        image = request.FILES['image']
        model = ThreeDModel(image=image)
        model.save()

        API_KEY = "msy_UHB6LVZqUdTmETLWZXlqNQ6tv9fF5ydQkrvP"
        API_URL = "https://api.meshy.ai/openapi/v1/image-to-3d"
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        with open(model.image.path, "rb") as image_file:
            base64_image = f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"

        payload = {
            "image_url": base64_image,
            "enable_pbr": True,
            "should_remesh": True,
            "should_texture": True
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        print("response",response_data)
        model.task_id = response_data['result']
        model.save()

        return redirect('vendor:list_models')
    return render(request, 'vendor/3d/create_model.html')



















from django.utils import timezone

def download_model(request, pk):
    model = ThreeDModel.objects.get(pk=pk)
    if model.downloaded or (timezone.now() - model.created_at).total_seconds() / 60 < 10:
        return HttpResponse("You can't download this model yet.")
    else:
        API_KEY = "msy_UHB6LVZqUdTmETLWZXlqNQ6tv9fF5ydQkrvP"
        API_URL = f"https://api.meshy.ai/openapi/v1/image-to-3d/{model.task_id}"
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        preview_model_url = response_data["model_urls"]["glb"]
        preview_model_response = requests.get(preview_model_url)
        preview_model_response.raise_for_status()

        model.downloaded = True
        model.save()
        messages.success(request, "Model downloaded successfully.")

        response = HttpResponse(preview_model_response.content, content_type='model/gltf-binary')
        response['Content-Disposition'] = 'attachment; filename="model.glb"'
        return response