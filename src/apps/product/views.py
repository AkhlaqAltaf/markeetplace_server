from django.core.serializers import serialize
from symtable import Class

from django.contrib import messages
from django.db.models import Min, Max
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponseBadRequest
from ..cart import cart
from ..cart.cart import Cart
from ..vendor.models import Vendor
from django import forms

# from .models import Category, CountryOrigin, Product, Media, SubCategory, Tag, WishListProduct, Order, OrderItem
from .forms import CategoryCreateForm, ProductForm, SubCategoryCreateForm, SubCategoryForm
from .forms import ProductForm, SubCategoryForm
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView

from django.shortcuts import render
from django.views import View
from .forms import SubCategoryForm
from .models import Category, Product, SubCategory

class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail/product_detail.html"
    context_object_name = "product"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        products_json = serialize('json', products)

        product = self.get_object()
        reviews = product.reviews.all()
        total_reviews = reviews.count()
        rating_distribution = {rating: 0 for rating in range(1, 6)}  # Initialize for ratings 1 to 5
        for review in reviews:
            print("REVIEW : ",review.rating)
            rating_distribution[review.rating] += 1
        rating_percentages = {
            rating: (count / total_reviews) * 100 if total_reviews > 0 else 0
            for rating, count in rating_distribution.items()
        }
        print(rating_percentages)
        # Add data to context
        context['rating_percentages'] = rating_percentages
        context['total_reviews'] = total_reviews
        # Add the JSON data to the context
        context['products'] = products_json
        return context


def create_subcategory(request):
    if request.method == "POST":
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            subcategory = form.save()
            return JsonResponse({'id': subcategory.id, 'name': subcategory.name}, status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)



        
class GetSubCategory(View):
    def get(self, request, category):
        print(f"Received category: {category}")  # Debug
        category_obj = Category.objects.filter(name=category).first()
        print(category_obj)
        if not category_obj:
            return JsonResponse({"error": "Category not found"}, status=404)

        sub_categories = SubCategory.objects.filter(category=category_obj)
        print(f"Subcategories: {sub_categories}")  # Debug
        data = [{"id": sub.pk, "name": sub.name} for sub in sub_categories]
        return JsonResponse({"subcategories": data})



class ProductDetail3DView(DetailView):
    model = Product
    template_name = "products/product_detail/3d_model.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        # Get the context from the superclass
        context = super().get_context_data(**kwargs)

        # Serialize all products to JSON format
        products = Product.objects.all()
        print(len(products))
        products_json = serialize('json', products)

        product = self.get_object()
        reviews = product.reviews.all()  # Assuming a related name `reviews` for the Product-Review relationship
        total_reviews = reviews.count()

        # Calculate rating percentages
        rating_distribution = {rating: 0 for rating in range(1, 6)}  # Initialize for ratings 1 to 5

        for review in reviews:
            print("REVIEW : ",review.rating)
            rating_distribution[review.rating] += 1  # Assuming `rating` is an attribute of Review

        rating_percentages = {
            rating: (count / total_reviews) * 100 if total_reviews > 0 else 0
            for rating, count in rating_distribution.items()
        }
        print(rating_percentages)
        # Add data to context
        context['rating_percentages'] = rating_percentages
        context['total_reviews'] = total_reviews
        # Add the JSON data to the context
        context['products'] = products_json
        return context








class AllProductsView(View):
    def get(self, request):
        # Get filter values from the request (multiple selected filters)
        filter_values = request.GET.getlist('filter')  # Categories selected via checkboxes
        price_filter = request.GET.get('price', None)  # Single price range filter

        # Get all unique categories for the filter checkboxes
        categories = Category.objects.all()

        # Get the minimum and maximum product prices
        min_price = Product.objects.aggregate(Min('price'))['price__min']
        max_price = Product.objects.aggregate(Max('price'))['price__max']

        # Ensure the prices are whole numbers
        if min_price is not None and max_price is not None:
            min_price = round(min_price)
            max_price = round(max_price)

            # Calculate the range and step size dynamically based on the price span
            price_range_span = max_price - min_price
            num_buckets = 3  # Default to 5 price ranges (this can be adjusted)
            
            if price_range_span > 500:
                num_buckets = 10  # More buckets for large price ranges
            elif price_range_span > 200:
                num_buckets = 7  # Use 7 buckets for medium price ranges

            price_step = round(price_range_span / num_buckets)

            # Create dynamic price ranges
            prices_range = {}
            for i in range(num_buckets):
                upper_limit = min_price + (i + 1) * price_step
                prices_range[f'bucket_{i + 1}'] = f'Under ${upper_limit}'
            prices_range['high'] = f'Under ${max_price}'  # Final high range

        else:
            prices_range = {}

        # Filter products based on selected categories
        products = Product.objects.all().select_related('category')

        if filter_values:
            products = products.filter(category__name__in=filter_values)

        # Filter by price range if selected
        if price_filter:
            price_parts = price_filter.split('_')
            if len(price_parts) == 2:
                bucket_index = int(price_parts[1]) - 1
                price_threshold = min_price + (bucket_index + 1) * price_step
                products = products.filter(price__lt=price_threshold)

        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, "products/includes/product_grid.html", {'products': products})

        # Pass the filtered data to the full page render
        context = {
            'products': products,
            'categories': categories,  # Pass all categories for the filter checkboxes
            'prices_range': prices_range,  # Dynamic price ranges
            'selected_filters': filter_values,  # Keep track of selected categories
            'selected_price': price_filter  # Keep track of the selected price range
        }
        return render(request, "products/all_products.html", context)





class CategoryProductsView(View):
    def get(self, request,id):
        category = get_object_or_404(Category, id=id)
        products = Product.objects.filter(category=category)
        context = {'products': products}
        return render(request, "products/all_products.html", context)




def search(request):
    query = request.GET.get('query', '') # second is default parameter which is empty
    products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return render(request, 'product/search.html', {'products':products, 'query': query})


# PRODUCT SEARCH VIEW

class ProductSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        products = Product.objects.filter(name__icontains=query)  # Adjust the field as necessary
        return render(request, 'products/all_products.html', {'products': products, 'query': query})

class ForgotEmailForm(forms.Form):
    email = forms.EmailField()

def forgot_email_view(request):
    if request.method == 'POST':
        form = ForgotEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Perform the email processing logic here (e.g., send a reset email).
            return HttpResponse(f"A reset email has been sent to {email}!")
    else:
        form = ForgotEmailForm()

    return render(request, 'accounts/forgetEmail.html', {'form': form})


class CategoryCreateView(View):
    def post(self, request, *args, **kwargs):
        form = CategoryCreateForm(request.POST, request.FILES)
        
        if form.is_valid():
            category = form.save()  # Save the new category to the database
            return JsonResponse({'status': 'success', 'message': 'Category created successfully!', 'category_id': category.id})
        else:
            # Return errors if the form is invalid
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors})

class SubCategoryCreateView(View):
    def post(self, request, *args, **kwargs):
        form = SubCategoryCreateForm(request.POST, request.FILES)
        
        if form.is_valid():
            # The category must be a valid category object, get it from the form's category field
            category = form.cleaned_data['category']
            
            # Create and save the subcategory
            subcategory = form.save()
            
            return JsonResponse({'status': 'success', 'message': 'Subcategory created successfully!', 'subcategory_id': subcategory.id})
        else:
            # Return errors if the form is invalid
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors})