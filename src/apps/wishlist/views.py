from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from src.apps.product.models import Product
from src.apps.wishlist.models import WishListProduct
from django.contrib.auth.mixins import LoginRequiredMixin

class WishListProductsCreateView(View):
    def post(self, request, id):
        user = request.user
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return HttpResponseBadRequest("Product does not exist.")

        if not WishListProduct.objects.filter(user=user, products=product).exists():
            wishlist, created = WishListProduct.objects.get_or_create(user=user)
            wishlist.products.add(product)
        messages.success(request, "Your action was successful!")
        return JsonResponse({'success': True})


class WishListProductsView(View):
    def get(self,request):
        user = request.user
        wishlists = WishListProduct.objects.filter(user=user)
        products = [wishlist.products.all() for wishlist in wishlists]
        print(products[0])
        context = {'products':products[0]}

        return render(request,'products/wishlist/wishlist.html',context)



class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        wishlist = get_object_or_404(WishListProduct, user=request.user)
        product = get_object_or_404(Product, id=product_id)

        # Remove the product from the wishlist
        wishlist.products.remove(product)
        messages.success(request, "Your action was successful!")
        return redirect('product:wishlist')