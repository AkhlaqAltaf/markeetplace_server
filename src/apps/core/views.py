from django.shortcuts import render
from django.views.generic import TemplateView

from src.apps.product.models import Category, Product, Media


# Create your views here.



class FrontPageView(TemplateView):
    template_name = "home/home.html"
    def get(self,request):

        products = Product.objects.all()

        categories = Category.objects.all()[0:8]
        context = {
            'products': products,
            'categories': categories
        }

        return render(request, self.template_name, context)


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