from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from ..vendor.models import Vendor

from .models import Category, CountryOrigin, Product, Media, SubCategory, Tag
from .forms import ProductForm, SubCategoryForm

# List View for Products
class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['media_form'] = MediaForm()  # Add the MediaForm to the context
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Handle multiple file uploads
        # media_form = MediaForm(self.request.POST, self.request.FILES)
        # if media_form.is_valid():
        #     files = self.request.FILES.getlist('files')  # Get the list of files
        #     for file in files:
        #         Media.objects.create(product=self.object, file=file)  # Save each file

        return response

# Product Update View
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy('product_list')

# Product Delete View
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy('product_list')

# Product Detail View
class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

# SubCategory Inline Creation View (AJAX)
def create_subcategory(request):
    if request.method == "POST":
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            subcategory = form.save()
            return JsonResponse({'id': subcategory.id, 'name': subcategory.name}, status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)





class CreateProduct(CreateView):
    def get(self, request, *args, **kwargs):
        
        categories = Category.objects.all()
        origins = CountryOrigin.objects.all()
        
        
        return render(request,template_name="vendor/add_product/addproduct.html",context={"categories":categories,'origins':origins})
    def post(self, request, *args, **kwargs):
        product = Product.objects.filter(name="cage").first()
        if product:
            print(product.tags.all())   
        else:
            print("Product not found")
        data = request.POST
        category_name = data.get("category")
        category_obj = Category.objects.filter(name=category_name).first()
        sub_category_obj = SubCategory.objects.filter(name=data.get("sub_category"), category=category_obj).first()
        # Validation Errors Dictionary
        
        errors = {}

        # Required fields
        required_fields = [
            'name', 'price', 'stock_quantity', 'category', 'sub_category', 'description'
        ]

        # Check for missing fields
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

        # Validate price (must be a positive number)
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
        # Validate stock_quantity (must be an integer)
        stock_quantity = data.get('stock_quantity')
        if stock_quantity:
            try:
                stock_quantity = int(stock_quantity)
                if stock_quantity < 0:
                    errors['stock_quantity'] = "Stock quantity must be 0 or more."
            except ValueError:
                errors['stock_quantity'] = "Stock quantity must be an integer."

        # Validate category (must exist)
        if not Category.objects.filter(name=category_name).exists():
            errors['category'] = "Invalid category selected."

        # Validate sub_category (must exist in the selected category)
        sub_category_name = data.get('sub_category')
        if not SubCategory.objects.filter(name=sub_category_name, category=category_obj).exists():
            errors['sub_category'] = "Invalid subcategory selected for the chosen category."

        # Check if there are validation errors
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # If data is valid, proceed with database insertion
        vendor = Vendor.objects.all().first()
        # Create the product
        product = Product.objects.create(
        name=data.get("name"),
        description=data.get("description"),
        category=category_obj,  # Make sure to use the category object, not just the name
        sub_category=sub_category_obj,  # You can get the subcategory object
        price=price,  # Ensure price is a float or None if validation passed
        discount_price=data.get("discount_price"),
        stock_quantity=stock_quantity,  # Ensure stock_quantity is an integer
        sku=data.get("sku"),
        currency=data.get("currency"),
        content=data.get("content"),
        vendor = vendor
        )
        
        if data.get("tags"):
         tag_string = data.get("tags")  # Assume this is an array of tag names
         tag_objs = []  # List to store Tag objects
         tag_names = tag_string.split(",")

        for tag_name in tag_names:         
        #  print(tag_name)
        # Check if the tag exists, otherwise create a new one
         tag_obj, created = Tag.objects.get_or_create(name=tag_name)
        # Append the tag object to the list
         tag_objs.append(tag_obj)

        # Set the tags for the product
        if tag_objs:
            product.tags.set(tag_objs)

        if data.get("country_of_origin"):
            origin_name = data.get("country_of_origin")  # Assuming country is passed as a single country name
            origin_obj = CountryOrigin.objects.filter(name=origin_name).first()  # Get the country object by name
        if origin_obj:
            product.country_of_origin.set([origin_obj]) 
        
        # # Assign the vendor after product creation
        # # product.vendor = vendor  # Ensure vendor is a valid Vendor object

        # # Assign tags and country_of_origin if available
        # if data.get("tags"):
       
        # if data.get("country_of_origin"):


        # Return success message
        return JsonResponse({'success': True, 'message': 'Product created successfully!'})
    
from django.core.serializers import serialize

        
class GetSubCategory(View):
    def get(self, request, category):
        category_obj = Category.objects.filter(name=category).first()
        if not category_obj:
            return JsonResponse({"error": "Category not found"}, status=404)

        sub_categories = SubCategory.objects.filter(category=category_obj)
        # Simplify the response to include only id and name
        data = [{"id": sub.pk, "name": sub.name} for sub in sub_categories]

        return JsonResponse({"subcategories": data})