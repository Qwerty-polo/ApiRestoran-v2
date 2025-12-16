from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from database.db import SessionDep
from models.models import CategoryModel, DishModel
from schemas.schemas import CategoryCreate, CategoryResponse,DishResponse,DishCreate
from routers.auth import security

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
    query = select(CategoryModel).options(selectinload(CategoryModel.dishes)) #Завантаж мені категорії
    # І ОДРАЗУ підтягни всі страви, які до них прив'язані
    result = await db.execute(query)
    return result.scalars().all()
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
    return new_dish
