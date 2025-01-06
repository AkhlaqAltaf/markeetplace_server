import json
import uuid

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
# Converting Title into Slug
from django.utils.text import slugify
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DetailView
from datetime import datetime

from django.core.serializers import serialize

from src.apps.product.forms import ProductForm
from src.apps.product.models import Category, SubCategory, Tag, Media, Product, ProductOffer, OrderOffer
from src.apps.vendor.forms import VendorForm, ProductOfferForm, OrderOfferForm
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
        return render(request, 'vendor/add_product/addproduct.html', context={"categories": categories,'form': form})
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

            return render(request, 'vendor/add_product/addproduct.html', context={"categories": categories ,'form': form})

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
        return render(request, 'vendor/add_product/add_bulk_products.html', context={"categories": categories})

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




def addProductTest(request):
    return render(request,template_name="vendor/add_product/addproduct.html")
def Checkout(request):
    return render(request,template_name="vendor/add_product/vendorcheckout.html")



def Register(request):
    return render(request, 'vendor/registration/registration2.html')




def storeAnalytics(request):
    return render(request, 'vendor/Analytics.html')
def OrderList(request):
    return render(request, 'vendor/order/orderlist.html')
def OrderDetails(request):
    return render(request, 'vendor/order/orderdetail.html')
def OrderStatus(request):
    return render(request, 'vendor/order/Status.html')
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





class RemoveProductView(View):
    def post(self, request, product_id):
        # Get the product or return a 404 if it doesn't exist
        product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)
        # Delete the product
        product.delete()
        # Add a success message
        messages.success(request, 'Product removed successfully.')

        # Redirect to the product list page
        return redirect('vendor:vendor_product_list')


class VendorProductListView(View):
    def get(self, request):
        # Get products associated with the current vendor
        products = Product.objects.filter(vendor=request.user.vendor)
        print("PRODUCTS",products)
        return render(request, 'vendor/products/productlist.html', {'products': products})








class EditProductView(UpdateView):
    model = Product
    form_class = ProductForm
    pk_url_kwarg = 'pk'

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get(self.pk_url_kwarg))
        form = self.get_form()

        if form.is_valid():
            # Save the product details
            self.object = form.save()
            print(f"FORM SAVED{ self.object}")
            # Handle image updates
            images_data = request.POST.getlist('images')
            if images_data:
                images_data = json.loads(images_data[0])  # Decode JSON string into a list
            else:
                images_data = []

            # Clear existing media files for the product
            Media.objects.filter(product=product).delete()

            # Save new images
            for image in images_data:
                file = self.convert_base64_image(image)
                if file:
                    Media.objects.create(product=product, file=file)

            return JsonResponse({'success': True, 'message': 'Product updated successfully'})
        else:
            print(f"NOT SUCCESS {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors})

    def convert_base64_image(self, base64_data):
        """
        Converts a base64 image string into a Django ContentFile.
        """
        data = next(iter(base64_data.values()))
        if data.startswith("data:image"):
            data = data.split(",")[1]
        try:
            file_data = base64.b64decode(data)
            content_file = ContentFile(file_data, name=f"{uuid.uuid4()}.jpg")
            return content_file
        except Exception as e:
            print(f"Error decoding base64 image: {e}")
            return None





class ProductDetailView(DetailView):
    model = Product
    template_name = "vendor/products/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Fetch all products and serialize them
        products = Product.objects.all()
        products_json = serialize('json', products)

        # Fetch product reviews
        reviews = product.reviews.all()
        total_reviews = reviews.count()
        rating_distribution = {rating: 0 for rating in range(1, 6)}  # Initialize for ratings 1 to 5

        # Calculate the rating distribution
        for review in reviews:
            rating_distribution[review.rating] += 1

        rating_percentages = {
            rating: (count / total_reviews) * 100 if total_reviews > 0 else 0
            for rating, count in rating_distribution.items()
        }

        # Fetch Product Offers for the product, category, and subcategory
        product_offers = ProductOffer.objects.filter(products=product)
        category_offers = ProductOffer.objects.filter(categories=product.category)
        subcategory_offers = ProductOffer.objects.filter(subcategories=product.subcategory)

        # Fetch Order Offers for the product, category, and subcategory
        product_order_offers = OrderOffer.objects.filter(products=product)
        category_order_offers = OrderOffer.objects.filter(categories=product.category)
        subcategory_order_offers = OrderOffer.objects.filter(subcategories=product.subcategory)

        # Add the offers to context
        context['product_offers'] = product_offers
        context['category_offers'] = category_offers
        context['subcategory_offers'] = subcategory_offers
        context['product_order_offers'] = product_order_offers
        context['category_order_offers'] = category_order_offers
        context['subcategory_order_offers'] = subcategory_order_offers

        # Add the ratings and review data to context
        context['rating_percentages'] = rating_percentages
        context['total_reviews'] = total_reviews

        # Add the JSON data of products to the context
        context['products'] = products_json

        return context


@login_required
def select_offer_type(request):
    """
    View to let the vendor choose which type of offer to create.
    """
    return render(request, 'vendor/offers/select_offer_type.html')

@login_required
def create_product_offer(request):
    """
    View to create a ProductOffer.
    Only shows products related to the logged-in vendor.
    """
    vendor = request.user.vendor  # Get the vendor associated with the logged-in user
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.vendor = vendor  # Associate the offer with the vendor
            offer.save()
            return redirect('vendor:create_product_offer')
    else:
        # Pass only the vendor's products to the form
        form = ProductOfferForm(vendor=vendor)
    return render(request, 'vendor/offers/create_product_offer.html', {'form': form})


@login_required
def create_order_offer(request):
    """
    View to create an OrderOffer with vendor-specific filtering.
    """
    vendor = request.user.vendor  # Get the vendor associated with the logged-in user
    if request.method == 'POST':
        form = OrderOfferForm(request.POST, vendor=vendor)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.vendor = vendor  # Associate the offer with the vendor
            offer.save()
            form.save_m2m()  # Save the many-to-many relationship (products)
            return redirect('vendor:create_order_offer')
    else:
        form = OrderOfferForm(vendor=vendor)
    return render(request, 'vendor/offers/create_order_offer.html', {'form': form})
# CREATING 3d MODEL


import requests
import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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