from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from database.db import SessionDep
from models.models import CategoryModel, DishModel
from schemas.schemas import CategoryCreate, CategoryResponse,DishResponse,DishCreate
from routers.auth import security

import json
from fastapi.encoders import jsonable_encoder
from database.redis_client import redis_client
router = APIRouter(tags=["menu"])

@router.post("/categories", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: SessionDep):
    new_cat = CategoryModel(name = category.name)
    db.add(new_cat)
    await db.commit()

    query = (
        select(CategoryModel)
        .options(selectinload(CategoryModel.dishes))
        .where(CategoryModel.id == new_cat.id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


#!!!повторить і подивиця як працює
@router.get("/categories", response_model=List[CategoryResponse])
async def get_menu(db: SessionDep):
    #add redis in our func
    # 🕵️ КРОК 1: Перевіряємо Redis (Кеш)
    # Ми шукаємо ключ "full_menu"
    cached_menu = await redis_client.get("full_menu")

    if cached_menu:
        print("Cashed menu was taken from redis !!!! ")
        # Redis зберігає тільки рядки, тому перетворюємо рядок назад у список
        return json.loads(cached_menu)

    print("Cashed menu was not taken from redis go to DB")
    query = select(CategoryModel).options(selectinload(CategoryModel.dishes)) #Завантаж мені категорії
    # І ОДРАЗУ підтягни всі страви, які до них прив'язані
    result = await db.execute(query)
    categories = result.scalars().all()

    # 💾 КРОК 3: Зберігаємо результат у Redis на майбутнє
    # Спочатку перетворюємо складні об'єкти SQLAlchemy в простий JSON
    data_to_save = jsonable_encoder(categories)

    # Записуємо в Redis. ex=60 означає, що кеш живе 60 секунд
    await redis_client.set("full_menu", json.dumps(data_to_save))

    return categories



#!!! повторить і подивиця як працює
@router.post("/dishes", response_model=DishResponse)
async def create_dish(dish: DishCreate, db: SessionDep):
    cat = await db.get(CategoryModel, dish.category_id) #Знайди мені категорію з таким ID,
    # який вказав користувач (dish.category_id)".
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    new_dish = DishModel(
        name = dish.name,
        description = dish.description,
        price = dish.price,
        category_id = dish.category_id,

    )
    db.add(new_dish)
    await db.commit()
    await db.refresh(new_dish)

    await redis_client.delete("full_menu")
    print("old kesh was deleted from menu")
    return new_dish
