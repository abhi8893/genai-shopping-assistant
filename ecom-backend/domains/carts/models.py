from core.database import Base
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey

__all__ = ("Cart", "CartItem")

class Cart(Base):

    __tablename__ = "cart"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)



class CartItem(Base):

    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    # cart_id = Column(Integer, ForeignKey("Cart.id"), nullable=False)
    # product_id = Column(Integer, ForeignKey("Product.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)


    

