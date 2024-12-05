from django.shortcuts import render
from src.apps.product.models import Category, Product

# Create your views here.

def frontpage(request):
    newest_products = Product.objects.all()[0:8]
    categories = Category.objects.all()[0:8]

    context = {
        'newest_products': newest_products,
        'categories':categories
    }
    return render(request, 'home/home.html', context)


def contactpage(request):
    return render(request, 'core/contact.html')