from core.database import Base
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sql_func

__all__ = ("CartDB", "CartItemDB")


class CartDB(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), default=sql_func.now(), nullable=False
    )

    cart_items = relationship("CartItemDB", back_populates="cart")
    user = relationship("UserDB", back_populates="carts")


class CartItemDB(Base):
    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(
        Integer, ForeignKey("product.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    cart = relationship("CartDB", back_populates="cart_items")
