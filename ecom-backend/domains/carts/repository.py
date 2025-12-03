from sqlalchemy.orm import Session
from domains.carts.models import CartDB, CartItemDB
from core.exceptions import ResourceNotFoundException
from abc import ABC, abstractmethod


class CartRepository(ABC):

    def __init__(self, db: Session):
        self.db = db 
    
    @abstractmethod
    def get_all(self, user_id: int, page: int, limit: int) -> list[CartDB]:
        pass

    @abstractmethod
    def get(self, cart_id: int) -> CartDB:
        pass

    @abstractmethod
    def create(self, cart: CartDB, user_id: int) -> CartDB:
        pass

    @abstractmethod
    def update(self, cart: CartDB) -> CartDB:
        pass

    @abstractmethod
    def delete(self, cart_id: int) -> None:
        pass

class SQLAlchemyCartRepository(CartRepository):

    def get_all(self, user_id: int, page: int, limit: int) -> list[CartDB]:
        carts = self.db.query(CartDB).filter(CartDB.user_id == user_id).offset((page - 1) * limit).limit(limit).all()
        if not carts:
            raise ResourceNotFoundException(f"Carts not found for user_id {user_id}")
        return carts

    def get(self, cart_id: int) -> CartDB:
        cart = self.db.query(CartDB).filter(CartDB.id == cart_id).first()
        if not cart:
            raise ResourceNotFoundException(f"Cart not found for cart_id {cart_id}")
        return cart

    def create(self, cart: CartDB, user_id: int) -> CartDB:
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)

        return cart

    def update(self, cart: CartDB) -> CartDB:
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)

        return cart

    def delete(self, cart_id: int) -> None:
        self.db.query(CartDB).filter(CartDB.id == cart_id).delete()
        self.db.commit()

    def empty_cart(self, cart_id: int) -> None:
        self.db.query(CartItemDB).filter(CartItemDB.cart_id == cart_id).delete()
        self.db.commit()
    

    