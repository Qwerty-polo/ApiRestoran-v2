from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database.db import engine, Base
from database.redis_client import check_redis

from routers import auth, menu, orders

from fastapi.security import HTTPBearer # цу для замочка

from sqladmin import Admin
from admin import UserAdmin, CategoryAdmin, DishAdmin, OrderAdmin, authentication_backend



bearer_scheme = HTTPBearer() # додали замочок у наш swager

# --- LIFESPAN (Життєвий цикл) ---
# Тут ми кажемо серверу: "Перед тим як почати роботу, створи таблиці"
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifespan - (Server is starting...)")

    # Створюємо таблиці (якщо їх немає)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database is ready!")

    await check_redis()

    yield # <-- Тут сервер працює і приймає запити

    print("Database is shutting down!")

# --- ІНІЦІАЛІЗАЦІЯ ---
# Передаємо наш lifespan у FastAPI
app = FastAPI(lifespan=lifespan, title="pizza Deliver v2")

# 🔥 ПІДКЛЮЧАЄМО АДМІНКУ 🔥
admin = Admin(app, engine, authentication_backend=authentication_backend)

# Додаємо сторінки, які ми створили в admin.py
admin.add_view(UserAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(DishAdmin)
admin.add_view(OrderAdmin)


# Підключаємо папку для картинок (щоб їх можна було відкрити в браузері)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(orders.router, dependencies=[Depends(bearer_scheme)])

@app.get("/")
async def root():
    return {"message": "Welcome to Delivery Api version 2"}
