from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, Media, SubCategory
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
