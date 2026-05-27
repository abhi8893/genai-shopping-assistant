from core.database import Base
from sqlalchemy import (
    Column,
    Float,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sqlfunc
from sqlalchemy.sql.sqltypes import TIMESTAMP


class ProductDB(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    subcategory_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=sqlfunc.now(), nullable=False
    )

    # Update the foreign key constraints
    __table_args__ = (
        ForeignKeyConstraint(
            ["category_id", "subcategory_id"],
            ["product_hierarchy.category_id", "product_hierarchy.subcategory_id"],
            ondelete="CASCADE",
        ),
    )

    product_hierarchy = relationship(
        "ProductHierarchyDB",
        back_populates="products",
    )


class ProductHierarchyDB(Base):
    __tablename__ = "product_hierarchy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer)
    subcategory_id = Column(Integer)
    category_name = Column(String, nullable=False)
    subcategory_name = Column(String, nullable=False)
    category_slug = Column(String, nullable=False)
    subcategory_slug = Column(String, nullable=False)

    # Add composite primary key
    __table_args__ = (UniqueConstraint("category_id", "subcategory_id"),)

    products = relationship("ProductDB", back_populates="product_hierarchy")
