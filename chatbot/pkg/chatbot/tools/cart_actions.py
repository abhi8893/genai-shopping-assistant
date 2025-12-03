from chatbot.external.ecom_api_client.resources.carts import CartsAPIClient
from chatbot.external.ecom_api_client.resources.carts.types import CartItemData, CartUpdateBody, CartCreateBody
import chatbot.types
from collections import Counter



# NOTE / TODO: Simplifying assumption of a single cart
# TODO: Change id to slug later

class Cart:

    def __init__(self, api_client: CartsAPIClient):
        self.api_client = api_client

    def init_cart(self):
        carts = self.api_client.get_all_carts()

        if not carts:
            cart = self.api_client.create_cart(
                cart_create_data=CartCreateBody(
                    cart_items=[]
                )
            )
        else:
            cart = carts[0]
            
        self._cart_id = cart.id
        

    def _get_counter_from_cart_items(self, cart_items: list[chatbot.types.CartItem]) -> Counter:

        counter = Counter()
        for cart_item in cart_items:
            cart_item = chatbot.types.CartItem.model_validate(cart_item)
            counter[cart_item.product_id] = cart_item.quantity
        return counter

    def _get_cart_items_from_counter(self, counter: Counter, as_dict=True) -> list[CartItemData] | list[dict]:
        cart_items = []
        for product_id, quantity in counter.items():
            cart_item = chatbot.types.CartItem(product_id=product_id, quantity=quantity)
            if as_dict:
                cart_item = cart_item.model_dump()

            cart_items.append(cart_item)
        return cart_items

    @property
    def counter(self) -> Counter:
        cart = self.api_client.get_cart(self._cart_id)
        cart_counter = self._get_counter_from_cart_items(cart.cart_items)
        return cart_counter

    def view_cart(self):
        return dict(self.counter)

    
    def add_item(self, product_id: int, quantity: int):
        counter = self.counter
        counter[product_id] += quantity
        self.api_client.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=self._get_cart_items_from_counter(counter, as_dict=True)
            ),
            cart_id=self._cart_id
        )
        return self

    
    def remove_item(self, product_id: int, quantity: int):
        counter = self.counter
        cur_qty = counter.get(product_id, 0)
        if cur_qty < quantity:
            raise ValueError("Not enough quantity in cart! Available: %s, Remove Request: %s", cur_qty, quantity)
        if cur_qty == quantity:
            del counter[product_id]
        else:
            counter[product_id] -= quantity

        self.api_client.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=self._get_cart_items_from_counter(counter, as_dict=True)
            ),
            cart_id=self._cart_id
        )
        return self

    def empty_item(self, product_id: int):
        counter = self.counter
        cur_qty = counter.get(product_id, 0)
        if cur_qty == 0:
            raise ValueError("Item not found in cart")
        
        counter[product_id] = 0
        self.api_client.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=self._get_cart_items_from_counter(counter, as_dict=True)
            ),
            cart_id=self._cart_id
        )

    def empty_cart(self):
        self.api_client.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=[]
            ),
            cart_id=self._cart_id
        )
        return self
        

