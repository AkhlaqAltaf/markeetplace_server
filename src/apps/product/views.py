from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .models import Category, CountryOrigin, Product, Media, SubCategory
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
        print(categories)
        
        return render(request,template_name="vendor/add_product/addproduct.html",context={"categories":categories,'origins':origins})
    
    def post(self, request, *args, **kwargs):
        # Assuming the data is in JSON format (commonly used in APIs)
        import json
        
        try:
            # Decode the request body
            data = "data"
            # print(request.method) 
            print(request.form())

            # product_name = request.POST.get('product_name')
            # price = request.POST.get('price')

            # print("Product Name:", product_name)
            # print("Price:", price)          
            # Print the incoming data to the console
            print("DATA: ", data)

            # You can handle the data here (e.g., validation, saving to the database, etc.)

            # Render a template after handling the POST request
            return render(request, "vendor/add_product/addproduct.html", {"data": data})
        
        except json.JSONDecodeError:
            # Handle the case where the body is not valid JSON
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    
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
        
