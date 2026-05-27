from typing import Literal

from core.exceptions import ResourceNotFoundException

from domains.carts.models import CartDB, CartItemDB
from domains.carts.repository import CartRepository
from domains.carts.schemas import CartCreate, CartData, CartUpdate
from domains.products.service import ProductService


class CartService:
    def __init__(self, repo: CartRepository, product_service: ProductService):
        self.repo = repo
        self.product_service = product_service

    def get_all(self, user_id: int, page: int, limit: int) -> list[CartData]:
        try:
            carts_db = self.repo.get_all(user_id, page, limit)
        except ResourceNotFoundException:
            new_cart_db = self.repo.create(CartDB(user_id=user_id, amount=0))
            carts_db = [new_cart_db]

        return [CartData.model_validate(cart_db) for cart_db in carts_db]

    def get(self, cart_id: int) -> CartData:
        cart_db = self.repo.get(cart_id)
        return CartData.model_validate(cart_db)

    def _prepare_cart_items(
        self,
        cart_input_data: CartUpdate | CartCreate,
        mode: Literal["create", "update"],
        cart_id: int | None = None,
    ) -> list[CartItemDB]:
        if mode == "update" and cart_id is None:
            raise ValueError("cart_id is required for update mode")

        if mode == "create" and cart_id is not None:
            raise ValueError("cart_id is not allowed for create mode")

        total_amount = 0
        cart_items_db = []
        for item in cart_input_data.cart_items:
            try:
                product = self.product_service.get(item.product_id)
            except ResourceNotFoundException as e:  # noqa: F841
                raise

            total_amount += product.price * item.quantity

            cart_item_db = CartItemDB(
                cart_id=cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                amount=product.price * item.quantity,
            )
            if mode == "update":
                cart_item_db.cart_id = cart_id

            cart_items_db.append(cart_item_db)

        return {"cart_items": cart_items_db, "amount": total_amount}

    def create(self, cart_create_data: CartCreate, user_id: int) -> CartData:
        cart_items_db_prep_result = self._prepare_cart_items(
            cart_create_data, mode="create"
        )

        cart_db = CartDB(
            user_id=user_id,
            amount=cart_items_db_prep_result["amount"],
            cart_items=cart_items_db_prep_result["cart_items"],
        )

        saved_cart = self.repo.create(cart_db)
        return CartData.model_validate(saved_cart)

    def empty_cart(self, cart_id: int) -> CartData:
        self.repo.empty_cart(cart_id)
        return self.get(cart_id)

    def update(self, cart_update_data: CartUpdate, cart_id: int) -> CartData:
        self.empty_cart(cart_id)
        cart_db = self.repo.get(cart_id)
        cart_items_db_prep_result = self._prepare_cart_items(
            cart_update_data, mode="update", cart_id=cart_id
        )
        cart_db.cart_items = cart_items_db_prep_result["cart_items"]
        cart_db.amount = cart_items_db_prep_result["amount"]

        updated_cart = self.repo.update(cart_db)

        return CartData.model_validate(updated_cart)

    def delete(self, cart_id: int) -> CartData:
        cart = self.get(cart_id)
        self.repo.delete(cart_id)
        return cart
