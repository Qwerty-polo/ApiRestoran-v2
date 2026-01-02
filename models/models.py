from sqlalchemy import String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from database.db import Base


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    # Зв'язок: Один юзер -> Багато замовлень
    orders: Mapped[List["OrderModel"]] = relationship(back_populates="user")

    def __str__(self):
        return self.username  # Тепер в адмінці буде написано просто "Pizza"


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Зв'язок: Одна категорія -> Багато страв
    # cascade="all, delete" означає: видалимо категорію -> видаляться всі її страви
    dishes: Mapped[List["DishModel"]] = relationship(
        back_populates="category", cascade="all, delete"
    )

    def __str__(self):
        return self.name


class DishModel(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float)
    image_url: Mapped[str] = mapped_column(String, nullable=False, default="")

    # Зовнішній ключ (посилання на категорію)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    # Зв'язок назад до категорії
    category: Mapped[CategoryModel] = relationship(back_populates="dishes")

    def __str__(self):
        return self.name


class OrderModel(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    total_price: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Хто замовив?
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(back_populates="orders")

    # Що всередині? (Список товарів у чеку)
    items: Mapped[List["OrderItemModel"]] = relationship(
        back_populates="order", cascade="all, delete"
    )


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)
    price: Mapped[float] = mapped_column(Float)

    # До якого замовлення належить
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped[OrderModel] = relationship(back_populates="items")

    # Яку страву взяли
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    dish: Mapped[DishModel] = relationship()
