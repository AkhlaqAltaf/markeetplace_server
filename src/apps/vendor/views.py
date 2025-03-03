import binascii
import json
import uuid
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView
from src.apps.accounts.models import CustomUser
from src.apps.product.forms import ProductForm, OfferForm, BrandRegistrationForm
from src.apps.product.models import Category, SubCategory, Media, Product, ProductOffer, OrderOffer, Brand
from src.apps.vendor.forms import VendorForm, ProductOfferForm, OrderOfferForm
from src.apps.vendor.models import Vendor
from .mixins import CheckVendorMixin
from ..order.models import Order, OrderItem
from django.db.models import Sum
from datetime import datetime, timedelta


class  Vendors(View):
    """THIS VIEW IS FOR SHOWING LIST OF REVIEWS"""
    template_name = 'vendors/vendors.html'
    def get(self, request):
        return render(request, self.template_name)


class BecomeVendorView(View):
    """BECOME VENDOR VIEW"""
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


class VendorSiteView(CheckVendorMixin, View):
    """VENDOR SITE VIEW AND ANALYTICS PAGE VIEW"""
    template_name = 'vendor/analytics/analytics.html'

    def get(self, request):
        vendor = request.user.vendor
        user = CustomUser.objects.filter(name=vendor).first()
        if not user:
            return render(request, self.template_name, {"error": "Vendor not found."})

        delivered_orders = Order.objects.filter(status='delivered', products__vendor=vendor).distinct()

        total_sales = 0
        total_cost = 0
        products = Product.objects.filter(vendor=vendor).order_by('-stock_quantity')

        for order in delivered_orders:
            order_items = order.orderitem_set.all()
            for order_item in order_items:
                product = order_item.product
                product_offer = ProductOffer.objects.filter(products=product).first()
                if product_offer:
                    if product_offer.discount_type == 'percentage':
                        total_sales += ((product.price - (
                                    product.price * (product_offer.discount_value / 100)))
                                        * order_item.quantity)
                    elif product_offer.discount_type == 'fixed':
                        total_sales += ((product.price - product_offer.discount_value)
                                        * order_item.quantity)
                else:
                    total_sales += product.price * order_item.quantity

                total_cost += product.price * order_item.quantity
        total_profit = total_sales - total_cost
        top_selling_products = OrderItem.objects.filter(order__products__vendor=
                                                        vendor).values('product').annotate(
            total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
        top_products = Product.objects.filter(id__in=[item['product']
                                                      for item in top_selling_products])

        under_review_count = Product.objects.filter(vendor=vendor, status='review').count()
        active_count = Product.objects.filter(vendor=vendor, status='active').count()
        out_of_stock_count = Product.objects.filter(vendor=vendor, stock_quantity=0).count()
        not_sold_count = sum(1 for product in products if product.get_total_sales() == 0)
        today = datetime.now()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=31)).replace(day=1)
        sales_revenue_data = []
        for day in range(1, (end_of_month - start_of_month).days):
            date = start_of_month + timedelta(days=day - 1)
            daily_sales = \
            OrderItem.objects.filter(order__products__vendor=vendor,
                                     order__created_at__date=date).aggregate(
                total_sales=Sum('quantity'))['total_sales'] or 0
            sales_revenue_data.append(daily_sales)

        context = {
            "products": products,
            "total_sales": total_sales,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "top_products": top_products,
            "under_review_count": under_review_count,
            "active_count": active_count,
            "out_of_stock_count": out_of_stock_count,
            "not_sold_count": not_sold_count,
            "sales_revenue_data": sales_revenue_data,
            "current_month": start_of_month.strftime("%B %Y"),
        }
        return render(request, self.template_name, context)






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
    
    
    
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

import json
import base64
from django.core.files.base import ContentFile
from datetime import datetime

class BaseProductView(View):
    """Base view for creating and editing products."""

    def get_categories(self):
        return Category.objects.all()
    def get_brands(self):
        return Brand.objects.all()

    def get_images(self, product):
        media_files = product.media.all()
        return [media.file.url for media in media_files]

    def handle_offers(self, product, request):
        discount_percentages = request.POST.getlist('discount_percentage')
        min_quantities = request.POST.getlist('min_quantity')
        max_quantities = request.POST.getlist('max_quantity')

        for i in range(len(discount_percentages)):
            offer_data = {
                'product': product,
                'discount_percentage': discount_percentages[i],
                'min_quantity': min_quantities[i],
                'max_quantity': max_quantities[i] if i < len(max_quantities) else None,
            }
            offer_form = OfferForm(offer_data)

            if offer_form.is_valid():
                offer_form.save()
            else:
                print(offer_form.errors)

    def handle_images(self, images_data, product):
        if images_data:
            images_data = json.loads(images_data[0])
        else:
            images_data = []
        for image in images_data:
            file = self.convert_base64_image(image)
            if file:
                Media.objects.create(product=product, file=file)
    def convert_base64_image(self, base64_data):
        if base64_data.startswith("data:image"):
            data = base64_data.split(",")[1]  # Remove the data:image part
            file_data = base64.b64decode(data)  # Decode the base64 string into binary data
            file_name = f"{datetime.now()}.jpg"  # Generate a unique file name
            return ContentFile(file_data, name=file_name)
        return None


class AddProductView(BaseProductView):
    """View for creating a single product."""

    def get(self, request, *args, **kwargs):
        form = ProductForm()
        offer_form = OfferForm()

        brands =self.get_brands()
        images = []
        product_id = request.GET.get('product_id')

        if product_id:
            product = get_object_or_404(Product, id=product_id)
            images = self.get_images(product)

        return render(request, 'vendor/add_product/addproduct.html', {
            "brands": brands,
            "form": form,
            "offer_form": offer_form,
            "images": json.dumps(images),
        })

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        images_data = request.POST.getlist('images')

        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()

            self.handle_offers(product, request)
            self.handle_images(images_data, product)

            return redirect('vendor:add')

        else:
            categories = self.get_categories()
            return render(request, 'vendor/add_product/addproduct.html', {
                "form": form,
                "images": json.dumps(images_data),
                "offer_form": OfferForm()
            })

class BulkUploadProductView(BaseProductView):
    """View for bulk uploading products."""

    def get(self, request, *args, **kwargs):
        categories = self.get_categories()
        return render(request, 'vendor/add_product/add_bulk_products.html', )

    def post(self, request, *args, **kwargs):

        try:
            products_data = json.loads(request.body)
            success_count = 0
            error_messages = []

            for product_data in products_data:
                form = ProductForm(product_data)
                if form.is_valid():
                    product = form.save(commit=False)
                    product.vendor = request.user.vendor
                    product.save()

                    # Handle offers if they exist
                    if 'offers' in product_data:
                        self.handle_offers(product, product_data)

                    # Handle images if they exist
                    if 'images' in product_data:
                        self.handle_images(product_data['images'], product)

                    success_count += 1  # Increment success count
                else:
                    # Collect error messages for each product
                    error_messages.append({
                        "product": product_data,
                        "errors": form.errors
                    })

            if error_messages:
                print("ERROR MESSAGES")
                messages.error(request,  f"message: {success_count} products uploade successfully :errors : {error_messages}")
                return JsonResponse({
                    "message": f"{success_count} products uploaded successfully!",
                    "errors": error_messages
                }, status=207)  # 207 Multi-Status for partial success

            return JsonResponse({"message": "All products uploaded successfully!"}, status=201)



        except json.JSONDecodeError:
            messages.error(request, "JSON decoding error")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            messages.error(request,str(e))
            return JsonResponse({"error": str(e)}, status=500)

    def handle_offers(self, product, product_data):
        if 'offers' in product_data:
            for offer in product_data['offers']:
                offer_data = {
                    'product': product,
                    'discount_percentage': offer.get('discount_percentage'),
                    'min_quantity': offer.get('min_quantity'),
                    'max_quantity': offer.get('max_quantity'),
                }
                offer_form = OfferForm(offer_data)

                if offer_form.is_valid():
                    offer_form.save()
                else:
                    print(offer_form.errors)

    def handle_images(self, images_data, product):
        if images_data:
            for image in images_data:
                file = self.convert_base64_image(image)
                if file:
                    Media.objects.create(product=product, file=file)

    def convert_base64_image(self, base64_data):
        if base64_data.startswith("data:image"):
            data = base64_data.split(",")[1]  # Remove the data:image part
            file_data = base64.b64decode(data)  # Decode the base64 string into binary data
            file_name = f"{timezone.now().timestamp()}.jpg"  # Generate a unique file name
            return ContentFile(file_data, name=file_name)
        return None


class EditProductView(BaseProductView):
    """View for editing an existing product."""

    def get(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(instance=product)
        offer_form = OfferForm()
        categories = self.get_categories()
        images = self.get_images(product)

        return render(request, 'vendor/add_product/edit_product.html', {
            "form": form,
            "offer_form": offer_form,
            "images": json.dumps(images)
        })

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, instance=product)
        images_data = request.POST.getlist('images')  # Get new images from the request

        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()

            # Handle offers if needed
            self.handle_offers(product, request)

            # Handle new images
            self.handle_images(images_data, product)

            return redirect('product:product-detail', product.id)

        else:
            categories = self.get_categories()
            images = self.get_images(product)
            return render(request, 'vendor/add_product/edit_product.html', {
                "form": form,
                "offer_form": OfferForm(),
                "images": json.dumps(images)
            })

class DeleteImageView(View):
    """View to delete an image from media."""
    def post(self, request, *args, **kwargs):
        print("REQUEST HIT...")
        image_url = request.POST.get('img_url')
        product = request.POST.get('product')
        media_all = Product.objects.get(id=product).media.all()


        print(image_url)
        if not image_url:
            return JsonResponse({'error': 'Image URL is required.'}, status=400)
        elif not product:
            return JsonResponse({'error': 'Product is required.'}, status=400)

        try:

            for media in media_all:
                print(media.file.url)
                if image_url != media.file.url:
                    print("MEDIA DELETED")
                    media.delete()
            return JsonResponse({'success': 'Image deleted successfully.'})

        except Media.DoesNotExist:
            return JsonResponse({'error': 'Image not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def register_brand(request):
    if request.method == 'POST':
        form = BrandRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('vendor:add')
    else:
        form = BrandRegistrationForm()

    return render(request, 'vendor/register_brand.html', {'form': form})

class AddBulkProductsView(View):

    def get(self, request):
        """Render the form for adding bulk products."""
        categories = Category.objects.all()
        return render(request, 'vendor/add_product/add_bulk_products.html')

    def post(self, request):
        """Process bulk product submissions."""
        try:
            data = json.loads(request.body)
            print(data)
            products = data.get("products", [])
            success_count, failed_products = self.process_bulk_products(products, request.user.vendor)

            return JsonResponse({
                "message": "Products processed successfully.",
                "success_count": success_count,
                "failed_products": failed_products
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Something went wrong: {str(e)}"}, status=500)

    def process_bulk_products(self, products, vendor):
        """Process and save multiple products."""
        success_count = 0
        failed_products = []

        for product_data in products:
            # Validate related data
            category, sub_category, country_of_origin, validation_error = self.validate_related_data(product_data)
            if validation_error:
                failed_products.append({
                    "product": product_data,
                    "error": validation_error
                })
                continue

            # Prepare form data and save the product
            product_data.update({
                'category': category.id,
                'sub_category': sub_category.id,
                'country_of_origin': country_of_origin.id
            })
            form = ProductForm(product_data)

            if form.is_valid():
                product = form.save(commit=False)
                product.vendor = vendor
                product.save()

                # Process and save product images
                images_data = product_data.get("images", [])
                self.process_images(images_data, product)

                success_count += 1
            else:
                failed_products.append({
                    "product": product_data,
                    "error": form.errors
                })

        return success_count, failed_products

    def validate_related_data(self, product_data):
        """Validate and retrieve related data."""
        category = Category.objects.filter(id=product_data.get('category')).first()
        sub_category = SubCategory.objects.filter(id=product_data.get('sub_category')).first()
        country_of_origin = CountryOrigin.objects.filter(id=product_data.get('country_of_origin')).first()

        if not category:
            return None, None, None, "Invalid category."
        if not sub_category:
            return None, None, None, "Invalid sub-category."
        if not country_of_origin:
            return None, None, None, "Invalid country of origin."

        return category, sub_category, country_of_origin, None

    @staticmethod
    def process_images(images_data, product):
        """Process and save base64-encoded images."""
        for image_base64 in images_data:
            file = AddBulkProductsView.convert_base64_image(image_base64)
            if file:
                Media.objects.create(product=product, file=file)

    @staticmethod
    def convert_base64_image(base64_data):
        """Convert a base64-encoded image to a Django ContentFile."""
        try:
            if base64_data.startswith("data:image"):
                base64_data = base64_data.split(",")[1]

            # Decode base64 data
            file_data = base64.b64decode(base64_data, validate=True)

            # Generate unique file name
            file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.jpg"
            return ContentFile(file_data, name=file_name)

        except binascii.Error as e:
            print(f"Base64 decoding error: {e}")
            return None
        except Exception as e:
            print(f"Error converting base64 image: {e}")
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
def checkout(request):
    return render(request,template_name="vendor/add_product/vendorcheckout.html")



def register(request):
    return render(request, 'vendor/registration/registration2.html')




def storeAnalytics(request):
    return render(request, 'vendor/analytics/analytics.html')
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








# class EditProductView(UpdateView):
#     model = Product
#     form_class = ProductForm
#     pk_url_kwarg = 'pk'
#
#     def post(self, request, *args, **kwargs):
#         product = get_object_or_404(Product, pk=kwargs.get(self.pk_url_kwarg))
#         form = self.get_form()
#
#         if form.is_valid():
#             # Save the product details
#             self.object = form.save()
#             print(f"FORM SAVED{ self.object}")
#             # Handle image updates
#             images_data = request.POST.getlist('images')
#             if images_data:
#                 images_data = json.loads(images_data[0])  # Decode JSON string into a list
#             else:
#                 images_data = []
#
#             # Clear existing media files for the product
#             Media.objects.filter(product=product).delete()
#
#             # Save new images
#             for image in images_data:
#                 file = self.convert_base64_image(image)
#                 if file:
#                     Media.objects.create(product=product, file=file)
#
#             return JsonResponse({'success': True, 'message': 'Product updated successfully'})
#         else:
#             print(f"NOT SUCCESS {form.errors}")
#             return JsonResponse({'success': False, 'errors': form.errors})
#
#     def convert_base64_image(self, base64_data):
#         """
#         Converts a base64 image string into a Django ContentFile.
#         """
#         data = next(iter(base64_data.values()))
#         if data.startswith("data:image"):
#             data = data.split(",")[1]
#         try:
#             file_data = base64.b64decode(data)
#             content_file = ContentFile(file_data, name=f"{uuid.uuid4()}.jpg")
#             return content_file
#         except Exception as e:
#             print(f"Error decoding base64 image: {e}")
#             return None





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