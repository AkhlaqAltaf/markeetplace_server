from django.core.serializers import serialize
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
        category_obj = Category.objects.filter(name=category).first()
        if not category_obj:
            return JsonResponse({"error": "Category not found"}, status=404)

        sub_categories = SubCategory.objects.filter(category=category_obj)
        # Simplify the response to include only id and name
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
        # Get filter values from request
        filter_values = request.GET.getlist('filter')  # Multiple selected filters
        price_filter = request.GET.get('price', None)

        # Get all unique categories
        categories = Category.objects.all()

        # Define the price ranges (modify as necessary)
        prices_range = {
            'low': 'Under $50',
            'medium': 'Under $100',
            'high': 'Under $200',
        }

        # Filter products based on category and price range
        products = Product.objects.all().select_related('category')

        if filter_values:
            products = products.filter(category__name__in=filter_values)

        if price_filter:
            if price_filter == 'low':
                products = products.filter(price__lt=50)
            elif price_filter == 'medium':
                products = products.filter(price__lt=100)
            elif price_filter == 'high':
                products = products.filter(price__lt=200)

        # If the request is AJAX, return the filtered products in a partial response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, "products/includes/product_grid.html", {'products': products})

        # Pass the filtered data to the full page render
        context = {
            'products': products,
            'categories': categories,  # Pass the unique categories to the template
            'prices_range': prices_range,  # Pass the price ranges to the template
            'selected_price': price_filter  # Pass the selected price filter to highlight the active one
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
