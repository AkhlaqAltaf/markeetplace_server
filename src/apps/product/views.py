from django import forms
from django.core.serializers import serialize
from django.db.models import Min, Max
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView

from .forms import CategoryCreateForm, SubCategoryCreateForm, BrandRegistrationForm
from .forms import SubCategoryForm
from .models import Category, Product, SubCategory, ProductOffer, OrderOffer, Brand


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        product_offers = None
        product_order_offers = None
        product_after_discount = 0

        try:
            # Fetch product offers and related order offers
            product_offers = ProductOffer.objects.filter(products=product).first()
            product_order_offers = OrderOffer.objects.filter(products=product)
            # PRODUCT OFFER: check for discount type and calculate discounted price
            if product_offers:
                if product_offers.discount_type == 'percentage':
                    product_after_discount = round(product.price - ((product.price / 100) * product_offers.discount_value), 1)
                else:
                    product_after_discount = product.price - product_offers.discount_value
            else:
                # If no offers found, set product price as is
                product_after_discount = product.price
        except ProductOffer.DoesNotExist:
            # Handle case where ProductOffer doesn't exist
            product_offers = None
            product_after_discount = product.price
            print("Product offer does not exist.")
        except OrderOffer.DoesNotExist:
            # Handle case where OrderOffer doesn't exist
            product_order_offers = None
            print("Order offer does not exist.")
        except Exception as e:
            # Catch any other exceptions and log them
            print(f"Error occurred: {str(e)}")
            raise Http404("Something went wrong while fetching offers.")

        # Add the fetched offers and calculated discount to context
        if product_after_discount == product.price:
            product_after_discount = 0

        # REVIEWS SECTION

        reviews = product.reviews.all()
        total_reviews = reviews.count()

        # Calculate rating percentages
        rating_distribution = {rating: 0 for rating in range(1, 6)}

        for review in reviews:
            print("REVIEW : ",review.rating)
            rating_distribution[review.rating] += 1
        rating_percentages = {
            rating: (count / total_reviews) * 100 if total_reviews > 0 else 0
            for rating, count in rating_distribution.items()
        }
        print(rating_percentages)
        print(reviews)
        context['reviews'] = reviews
        context['total_reviews'] = total_reviews
        context['rating_percentages'] = rating_percentages
        context['products'] = Product.objects.all()[:8]
        context['product_offers'] = product_offers
        context['discount'] = product_after_discount
        context['product_order_offers'] = product_order_offers
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
        reviews = product.reviews.all()
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


class BrandPageView(View):
    def get(self,request):
        brands = Brand.objects.all()
        return render(request,'brands/brands.html',{'brands':brands})


class AllProductsView(View):
    def get(self, request):
        filter_values = request.GET.getlist('filter')  # Category & Subcategory filters
        price_filter = request.GET.get('price', None)
        brand_filter = request.GET.getlist('brand')  # Get selected brand filters
        search_query = request.GET.get('q', '')  # Search query

        categories = Category.objects.all()
        brands = Brand.objects.all()  # Fetch all brands

        # Get the min and max price of products
        min_price = Product.objects.aggregate(Min('price'))['price__min']
        max_price = Product.objects.aggregate(Max('price'))['price__max']

        if min_price is not None and max_price is not None:
            min_price = round(min_price)
            max_price = round(max_price)

            price_range_span = max_price - min_price
            num_buckets = 3

            if price_range_span > 500:
                num_buckets = 10
            elif price_range_span > 200:
                num_buckets = 7

            price_step = round(price_range_span / num_buckets)
            prices_range = {
                f'bucket_{i + 1}': f'Under ${min_price + (i + 1) * price_step}'
                for i in range(num_buckets)
            }
            prices_range['high'] = f'Under ${max_price}'
        else:
            prices_range = {}

        # Fetch products and apply filters
        products = Product.objects.all().select_related('category', 'sub_category', 'brand')

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(brand__name__icontains=search_query) |  # Search by brand name
                Q(description__icontains=search_query)
            )

        if filter_values:  # Filter by category and subcategory
            products = products.filter(Q(category__id__in=filter_values) | Q(sub_category__id__in=filter_values))

        if price_filter:  # Apply price range filter
            price_parts = price_filter.split('_')
            if len(price_parts) == 2:
                bucket_index = int(price_parts[1]) - 1
                price_threshold = min_price + (bucket_index + 1) * price_step
                products = products.filter(price__lt=price_threshold)

        if brand_filter:  # Apply brand filter
            products = products.filter(brand__id__in=brand_filter)

        # Calculate discounts for products
        allProductOffers = ProductOffer.objects.all()
        discounts = []
        for product in products:
            product_offer = allProductOffers.filter(products=product).first()
            if product_offer:
                if product_offer.discount_type == 'percentage':
                    discount_value = round(product.price - (product.price * (product_offer.discount_value / 100)), 2)
                elif product_offer.discount_type == 'fixed':
                    discount_value = max(product.price - product_offer.discount_value, 0)
                else:
                    discount_value = None
            else:
                discount_value = None
            discounts.append(discount_value)

        # Check for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, "products/includes/product_grid.html", {'products': products})

        # Pass data to template
        context = {
            'products_with_discounts': zip(products, discounts),
            'categories': categories,
            'brands': brands,  # Pass brands to the template
            'prices_range': prices_range,
            'selected_filters': filter_values,
            'selected_brands': brand_filter,  # Track selected brands
            'selected_price': price_filter,
            'search_query': search_query,
        }
        return render(request, "products/all_products/all_products.html", context)
class CategoryProductsView(View):
    def get(self, request,id):
        category = get_object_or_404(Category, id=id)
        products = Product.objects.filter(category=category)
        context = {'products': products}
        return render(request, "products/all_products/all_products.html", context)




def product_search(request):
    query = request.GET.get('q')  # Get the search query from the request
    products = Product.objects.all()  # Start with all products

    if query:
        # Filter products based on name, brand, or description
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query)
        )
    print("PRODUCTS...")
    print(products)
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/all_products/all_products.html', context)

# PRODUCT SEARCH VIEW


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