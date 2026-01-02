from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 1. URL Бази Даних
# Використовуємо SQLite для початку (це файл).
# check_same_thread=False потрібен тільки для SQLite.
SQL_URL = "sqlite+aiosqlite:///./menu.db"

# 2. Двигун (Engine)
# echo=True змусить базу писати в терміналі всі SQL-запити (зручно для дебагу)
engine = create_async_engine(
    SQL_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# 3. Фабрика Сесій
# expire_on_commit=False — ОБОВ'ЯЗКОВО для асинхронності!
# Щоб об'єкти не "зникали" з пам'яті після збереження.
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 4. Базова модель (Base)
# Всі наші таблиці будуть наслідуватися від цього класу.
class Base(DeclarativeBase):
    pass


# 5. Dependency (Залежність для FastAPI)
# Ця функція відкриває сесію, віддає її роутеру і закриває.
async def get_db():
    async with SessionLocal() as session:
        yield session


# 6. Створюємо готовий Тип Даних (Annotated)
# Щоб у роутерах писати просто: db: SessionDep
SessionDep = Annotated[AsyncSession, Depends(get_db)]
