from sqladmin import ModelView
from starlette.responses import Response

from models.models import UserModel, CategoryModel, DishModel, OrderModel

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select
from routers.auth import verify_password
from database.db import SessionLocal

# 🔥 СТВОРЮЄМО КЛАС ЗАХИСТУ 🔥
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # 1. Отримуємо дані з форми (те, що ввів юзер)
        form = await request.form()
        username, password = form["username"], form["password"]

        # 2. Відкриваємо сесію до БД (оскільки ми не в роутері, робимо це вручну)
        async with SessionLocal() as session:
            query = select(UserModel).where(UserModel.username == username)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

        # 3. Перевіряємо пароль
        if user and verify_password(password, user.hashed_password):
            # Якщо ок — записуємо токен у сесію браузера
            request.session.update({"token": "admin_logged_in"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        # Очищаємо сесію при виході
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:

        token = request.session.get("token")
        return bool(token)

# Ініціалізуємо наш захист (секретний ключ придумай будь-який)
authentication_backend = AdminAuth(secret_key="super_secret_key")



# 1. Налаштування для Юзерів
class UserAdmin(ModelView, model = UserModel):
    column_list = [UserModel.id, UserModel.username]# Показувати тільки ID та Ім'я
    column_searchable_list = [UserModel.username]# Дозволити пошук по імені
    icon = "fa-solid fa-user"   # Іконка чоловічка
    name = "User"
    name_plural = "Users" #назва іконки


# 2. Налаштування для Категорій
class CategoryAdmin(ModelView, model=CategoryModel):
    column_list = [CategoryModel.id, CategoryModel.name]
    icon = "fa-solid fa-list"
    name = "Category"
    name_plural = "Categories"


# 3. Налаштування для Страв
class DishAdmin(ModelView, model=DishModel):
    column_list = [DishModel.id, DishModel.name, DishModel.price, DishModel.category]
    column_searchable_list = [DishModel.price] # Можна сортувати по ціні
    icon = "fa-solid fa-utensils" # Іконка виделки з ножем
    name = "Dish"
    name_plural = "Dishes"


# 4. Налаштування для Замовлень
class OrderAdmin(ModelView, model= OrderModel):
    column_list = [OrderModel.id, OrderModel.status, OrderModel.total_price, OrderModel.created_at]
    icon = "fa-solid fa-cart-shopping" # Іконка кошика
    name = "Order"
    name_plural = "Orders"
    can_create = False # Заборонимо створювати замовлення тут (це роблять клієнти)

