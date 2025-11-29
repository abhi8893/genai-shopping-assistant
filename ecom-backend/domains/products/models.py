from core.database import Base
from sqlalchemy import Integer, Column, ForeignKey, String, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class Product(Base):

    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("product_hierarchy.category_id", ondelete="CASCADE"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("product_hierarchy.subcategory_id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)

    product_hierarchy = relationship("ProductHierarchy", back_populates="products")


class ProductHierarchy(Base):

    __tablename__ = "product_hierarchy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, autoincrement=True)
    subcategory_id = Column(Integer, autoincrement=True)
    category_name = Column(String, nullable=False)
    subcategory_name = Column(String, nullable=False)

    products = relationship("Product", back_populates="product_hierarchy")


    
    