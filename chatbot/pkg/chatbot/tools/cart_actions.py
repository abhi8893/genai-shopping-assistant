from chatbot.external.ecom_api_client.client import EcomAPIClient
from chatbot.external.ecom_api_client.resources.carts.types import CartItemData, CartUpdateBody, CartCreateBody, CartResponse
from chatbot.external.ecom_api_client.resources.products.client import ProductsAPIClient
import chatbot.types
from collections import Counter
# import functools
# from copy import deepcopy



# TODO: Implement product info caching (before altering the API design)
# def refresh_product_info(func):

#     @functools.wraps(func)
#     def modfunc(self, *args, **kwargs):
#         pass


# class ReversibleMap:

#     def __init__(self, mapping: dict):
#         self._k2v_map = deepcopy(mapping)
#         self._v2k_map = {v: k for k, v in mapping.items()}


#     def update(self, mapping: dict):
#         self.update_by_key(mapping)

#     def update_by_key(self, mapping: dict):
#         self._k2v_map.update(mapping)
#         self._v2k_map = {v: k for k, v in self._k2v_map.items()}

#     def update_by_value(self, mapping: dict):
#         self._v2k_map.update(mapping)
#         self._k2v_map = {k: v for k, v in self._v2k_map.items()}

#     def get_by_key(self, key):
#         return self._k2v_map.get(key)

#     def get_by_value(self, value):
#         return self._v2k_map.get(value)

#     @property
#     def forward(self):
#         return self._k2v_map

#     @property
#     def reverse(self):
#         return self._v2k_map

# class ProductCache:
#     def __init__(self, api_client: ProductsAPIClient):
#         self.id_to_slug = ReversibleMap({})
#         self.api_client = api_client


#     def update_id_to_slug(self, cart_items: list[chatbot.types.CartItem]):

#         for cart_item in cart_items:
#             if cart_item.product_id not in self.id_to_slug.forward:
#                 product_response = self.api_client.get_by_id(cart_item.product_id)
#                 self.id_to_slug.update_by_key({cart_item.product_id: product_response.slug})


# NOTE / TODO: Simplifying assumption of a single cart

class CartInterface:

    def __init__(self, api_client: EcomAPIClient):
        self.api_client = api_client
    
    def init_cart(self):
        carts = self.api_client.carts.get_all_carts()

        if not carts:
            cart = self.api_client.carts.create_cart(
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
            product_slug = self.api_client.products.get_by_id(cart_item.product_id).slug
            counter[product_slug] = cart_item.quantity
        return counter

    def _get_cart_items_from_counter(self, counter: Counter, as_dict=True) -> list[CartItemData] | list[dict]:
        cart_items = []
        for product_slug, quantity in counter.items():
            product_id = self.api_client.products.get_by_slug(product_slug).id
            cart_item = chatbot.types.CartItem(product_id=product_id, quantity=quantity)
            if as_dict:
                cart_item = cart_item.model_dump()

            cart_items.append(cart_item)
        return cart_items

    @property
    def counter(self) -> Counter:
        cart = self.api_client.carts.get_cart(self._cart_id)
        cart_counter = self._get_counter_from_cart_items(cart.cart_items)
        return cart_counter

    def view_cart(self):
        return dict(self.counter)

    
    def add_item(self, product_slug: str, quantity: int):
        counter = self.counter
        counter[product_slug] += quantity
        self.api_client.carts.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=self._get_cart_items_from_counter(counter, as_dict=True)
            ),
            cart_id=self._cart_id
        )
        return self

    
    def remove_item(self, product_slug: str, quantity: int):
        counter = self.counter
        cur_qty = counter.get(product_slug, 0)
        if cur_qty < quantity:
            raise ValueError("Not enough quantity in cart! Available: %s, Remove Request: %s", cur_qty, quantity)
        if cur_qty == quantity:
            del counter[product_slug]
        else:
            counter[product_slug] -= quantity

        self.api_client.carts.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=self._get_cart_items_from_counter(counter, as_dict=True)
            ),
            cart_id=self._cart_id
        )
        return self

    def empty_item(self, product_slug: str):
        counter = self.counter
        cur_qty = counter.get(product_slug, 0)
        if cur_qty == 0:
            raise ValueError("Item not found in cart")
        
        counter[product_slug] = 0
        self.api_client.carts.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=self._get_cart_items_from_counter(counter, as_dict=True)
            ),
            cart_id=self._cart_id
        )

    def empty_cart(self):
        self.api_client.carts.update_cart(
            cart_update_data=CartUpdateBody(
                cart_items=[]
            ),
            cart_id=self._cart_id
        )
        return self
        



