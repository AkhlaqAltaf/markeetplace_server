from django.conf import settings
from django.contrib import messages
from src.apps.product.models import Product


class Cart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)
            offer_id = self.cart[str(p)]['offer']
            quantity = self.cart[str(p)]['quantity']
            self.cart[str(p)]['total_price'] = self.cart[str(p)]['product'].get_total_price(quantity, offer_id)
            yield self.cart[str(p)]

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def update_quantity(self, request, product_id, quantity):
        product_id = str(product_id)
        product = Product.objects.get(pk=product_id)

        if product_id in self.cart:
            new_quantity = self.cart[product_id]['quantity'] + quantity

            # Check if the new quantity exceeds stock
            if new_quantity > product.stock_quantity:
                messages.error(request, f"Cannot update quantity. Only {product.stock_quantity} available.")
                return

            if new_quantity <= 0:
                self.remove(product_id)
            else:
                self.cart[product_id]['quantity'] = new_quantity
            self.save()

    def cart_length(self):
        return len(self.cart)

    def add_with_specific_quantity(self, request, product_id, quantity, offer_id):
        product_id = str(product_id)
        product = Product.objects.get(pk=product_id)

        # Check if the requested quantity exceeds stock
        if product.stock_quantity < quantity:
            messages.error(request,
                           f"Cannot add {quantity} of {product.name}. Only {product.stock_quantity} available.")
            return

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': quantity, 'id': product_id, 'offer': offer_id}
            self.save()
            messages.success(request, f"Product added successfully with quantity: {quantity}")
        else:
            messages.info(request, "This product is already in the cart.")


    def add(self, request, product_id, quantity=1, update_quantity=False):
        """ADD INTO CART FIRST TIME...."""
        product_id = str(product_id)
        product = Product.objects.get(pk=product_id)
        new_quantity = quantity

        # Check if the new quantity exceeds stock
        if new_quantity > product.stock_quantity:
            messages.error(request,
                           f"Cannot add {new_quantity} of {product.name}. Only {product.stock_quantity} available.")
            return

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'id': product_id, 'offer': None}


        else:
            messages.info(request, "This product is already in the cart.")
            return

        self.cart[product_id]['quantity'] = new_quantity

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product_id)

        self.save()

    def remove(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_total_cost(self):
        total_cost = sum(item['total_price'] for item in self.cart.values())
        return round(total_cost, 2)