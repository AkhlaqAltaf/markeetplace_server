from django.conf import settings

from src.apps.product.models import Product, ProductOffer


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
            # Fetch product offers for discount
            self.cart[str(p)]['product_offers'] = self.get_product_offers(self.cart[str(p)]['product'])

            # Apply the discount if any
            self.cart[str(p)]['discounted_price'] = self.calculate_discounted_price(
                self.cart[str(p)]['product'],
                self.cart[str(p)]['product_offers']
            )

        for item in self.cart.values():
            item['total_price'] = item['discounted_price'] * item['quantity']

            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        # Check if the product is already in the cart
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'id': product_id}

        # Update quantity
        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)
        else:
            self.cart[product_id]['quantity'] = int(quantity)

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
        total_cost = 0
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)
            self.cart[str(p)]['product_offers'] = self.get_product_offers(self.cart[str(p)]['product'])
            self.cart[str(p)]['discounted_price'] = self.calculate_discounted_price(
                self.cart[str(p)]['product'],
                self.cart[str(p)]['product_offers']
            )
            total_cost += self.cart[str(p)]['discounted_price'] * self.cart[str(p)]['quantity']

        return total_cost

    def get_product_offers(self, product):
        try:
            # Fetch product offers related to the product
            product_offers = ProductOffer.objects.filter(products=product).first()
            return product_offers
        except ProductOffer.DoesNotExist:
            return None

    def calculate_discounted_price(self, product, product_offers):
        # Apply discount logic
        if product_offers:
            if product_offers.discount_type == 'percentage':
                return round(product.price - ((product.price / 100) * product_offers.discount_value), 1)
            else:
                return product.price - product_offers.discount_value
        else:
            # If no product offer is found, return original price
            return product.price


        
