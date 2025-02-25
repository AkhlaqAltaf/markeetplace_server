from itertools import product
from django.conf import settings
from django.contrib import messages
from src.apps.product.models import Product, ProductOffer

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def update_quantity(self, product_id, quantity):
        product_id = str(product_id)
        print("UPDATING QUANTITY...........")
        # Check if the product is in the cart
        if product_id in self.cart:
            # Update the quantity
            self.cart[product_id]['quantity'] += quantity

            # Remove the product if quantity is 0 or less
            if self.cart[product_id]['quantity'] <= 0:
                self.remove(product_id)

            self.save()

    def __iter__(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)
            # Fetch product offers for discount

            # Calculate total price using the get_total_price method
            offer_id = self.cart[str(p)]['offer']  # Get the offer ID if it exists
            quantity = self.cart[str(p)]['quantity']
            self.cart[str(p)]['total_price'] = self.cart[str(p)]['product'].get_total_price(quantity, offer_id)

            yield self.cart[str(p)]

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def cart_length(self):
        return len(self.cart)

    def add_with_specific_quantity(self, request, product_id, quantity, offer_id):
        if product_id not in self.cart:
            print("PRODUCT ADD WITH QUANTITY")
            self.cart[product_id] = {'quantity': quantity, 'id': product_id, 'offer': offer_id}
            self.save()
            messages.success(request, f"Product Added Successfully with Quantity: {quantity}")
        else:
            print ("THIS IS ALREADY IN CART")
            messages.info(request=request, message="THIS IS ALREADY IN CART")

    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        # Check if the product is already in the cart
        if product_id not in self.cart:
            print("PRODUCT IS NOT IN CART....")
            self.cart[product_id] = {'quantity': 0, 'id': product_id, 'offer': None}

        # Update quantity
        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)
        else:
            print("PRODUCT IS IN CART....")
            self.cart[product_id]['quantity'] += int(quantity)

        # Fetch and apply discount if quantity > 0
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
        return round(total_cost, 2)  # Return total cost rounded to 2 decimal places