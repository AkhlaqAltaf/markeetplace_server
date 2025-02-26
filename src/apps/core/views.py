from django.shortcuts import render
from django.views.generic import TemplateView
from src.apps.product.models import Category, Product, TopPageProduct, LandingPageProduct


class LandingPageView(TemplateView):
    """LANDING PAGE VIEW"""
    template_name = "home/home.html"
    def get(self,request, *args, **kwargs):
        products = Product.objects.all()[0:12]
        categories = Category.objects.all()[0:8]
        top_product =LandingPageProduct.objects.first()
        context = {
            'products': products,
            'categories': categories,
            'top_product': top_product

        }
        return render(request, self.template_name, context)


class ContactUsView(TemplateView):
    """CONTACT US PAGE VIEW"""
    template_name = "core/contact.html"
    def get(self,request, *args, **kwargs):
        return render(request, self.template_name)


class AboutUsView(TemplateView):
    """ABOUT PAGE VIEW"""
    template_name = "core/about.html"
    def get(self,request, *args, **kwargs):
        return render(request, self.template_name)
