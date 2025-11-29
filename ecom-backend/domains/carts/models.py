from core.database import Base
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

__all__ = ("Cart", "CartItem")

class Cart(Base):

    __tablename__ = "cart"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)

    cart_items = relationship("CartItem", back_populates="cart")
    user = relationship("User", back_populates="carts")



class CartItem(Base):

    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    cart = relationship("Cart", back_populates="cart_items")


    

