from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from src.apps.cart.cart import Cart
from src.apps.order.models import Order, OrderItem
from src.apps.product.models import Product

# ORDER PLACE VIEW

class PlaceOrderView(View):
    def post(self, request):
        cart = Cart(request)
        user = request.user
        address = request.POST.get('addressInput')
        street = request.POST.get('street')
        city = request.POST.get('city')
        country = request.POST.get('country')
        postal_code = request.POST.get('postalCode')
        payment_method = request.POST.get('payment_method')

        if not all([address, street, city, country, postal_code, payment_method]):
            return HttpResponseBadRequest("All fields are required.")

        order = Order.objects.create(
            user=user,
            address=address,
            city=city,
            country=country,
            postal_code=postal_code,
            payment_method=payment_method
        )
        order.save()
        print("ORDER SAVED...........")
        for product_id, item in cart.cart.items():
            quantity = item['quantity']

            try:
                product = Product.objects.get(id=product_id)  # Get the product
                if product.stock_quantity < quantity:
                    return HttpResponseBadRequest(f"Not enough stock for product ID {product_id}. Available: {product.stock_quantity}")

                # Create order item
                order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity)
                order_item.save()
                print("ORDER SAVED.......")
                product.stock_quantity -= quantity
                product.save()

            except Product.DoesNotExist:
                return HttpResponseBadRequest(f"Product with ID {product_id} does not exist.")

        cart.clear()
        messages.success(request, "Your order was successful!")
        return redirect('/')

    # ORDER DETAIL VIEW

class OrderDetailView(View):
    def get(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            messages.error(request, "Order does not exist.")
            return HttpResponseBadRequest("Order does not exist or you do not have permission to view it.")

        return render(request, 'order/order_detail.html', {'order': order})




              # ORDER LIST VIEW

class UserOrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return render(request, 'order/order_list.html', {'orders': orders})



# CANCEL ORDER VIEW


class CancelOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            if order.status == 'pending':  # Allow cancellation only if the order is pending
                order.status = 'cancelled'
                order.save()
                messages.success(request, "Your order has been cancelled.")
                return redirect('product:user_order_list')
            else:
                messages.success(request, "Your order has been cancelled.")
                return redirect('product:user_order_list')
        except Order.DoesNotExist:
            messages.error(request, "Your order does not exist.")
            return redirect('order:user_order_list')


class UpdateOrderStatusView(View):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order does not exist.")

        new_status = request.POST.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return HttpResponseBadRequest("Invalid status.")

        order.status = new_status
        order.save()

        return redirect('order:orders')

class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        # Get all products for the vendor
        vendor_products = Product.objects.filter(vendor=request.user.vendor)  # Assuming the user has a related Vendor
        # Get all orders that contain the vendor's products
        orders = Order.objects.filter(products__in=vendor_products).distinct()
        print("ORDERS ,",orders)
        return render(request, 'vendor/order/../../../templates/order/orderlist.html', {'orders': orders})


class OrderFilterView(LoginRequiredMixin, View):
    def get(self, request, status):
        # Get all products for the vendor
        vendor_products = Product.objects.filter(vendor=request.user.vendor)  # Assuming the user has a related Vendor
        # Filter orders based on status
        if status == 'ALL':
            orders = Order.objects.filter(products__in=vendor_products).distinct()
        else:
            orders = Order.objects.filter(products__in=vendor_products, status=status.lower()).distinct()
        return render(request, 'vendor/order/../../../templates/order/orderlist.html', {'orders': orders})


