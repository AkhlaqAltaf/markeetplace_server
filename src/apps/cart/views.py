import stripe
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from marketplace_server import settings
from .cart import Cart
from .forms import CheckoutForm
from ..order.utilities import checkout, notify_customer, notify_vendor
from ..product.models import Product


def success(request):
    return render(request, 'cart/success.html')

class AddToCartView(View):
    """ADD TO CART VIEW """

    def post(self, request, id,quantity):
        product = get_object_or_404(Product, id=id)
        print(product)
        cart = Cart(request)
        cart.add(request=request,product_id=product.id, quantity=quantity)
        return  JsonResponse({'success': True})

class AddToCartWithOffer(View):
    """THIS VIEW USE FOR IF:
     """
    def get(self):
        pass
    def post(self, request,id,quantity,offerid):
        cart = Cart(request)
        cart.add_with_specific_quantity(request,id,quantity,offerid)
        return JsonResponse({'success': True})




def cart_detail(request):
    cart = Cart(request)
    print("NOT POST")
    form = CheckoutForm()
    print("JUST REMOVE FROM CART")
    remove_from_cart = request.GET.get('remove_from_cart', '')
    change_quantity = request.GET.get('change_quantity', '')
    quantity = request.GET.get('quantity', 0)

    if remove_from_cart:
        cart.remove(remove_from_cart)
        return redirect('cart:cart')

    if change_quantity:
        cart.update_quantity(request,change_quantity, int(quantity))
        print("CART ACCESS")

        return redirect('cart:cart')

    return render(request, 'cart/cart.html', {'form': form, 'stripe_pub_key': settings.STRIPE_PUB_KEY})
