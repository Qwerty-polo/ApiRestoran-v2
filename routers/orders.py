from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from database.db import SessionDep
from models.models import OrderModel, OrderItemModel, DishModel
from schemas.schemas import OrderCreate, OrderResponse
from routers.auth import security

router = APIRouter(tags=["Orders"])


# !!!!!!!! повторить і зрозуміть як все працює
@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: SessionDep,
    user_token=Depends(security.access_token_required),
):
    user_id = int(user_token.sub)

    new_order = OrderModel(user_id=user_id, total_price=0.0)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    current_total = 0.0

    for item in order_data.items:
        dish = await db.get(DishModel, item.dish_id)
        if not dish:
            raise HTTPException(
                status_code=404, detail=f"Dish {item.dish_id} not found"
            )

        row_price = dish.price * item.quantity
        current_total += row_price

        order_item = OrderItemModel(
            order_id=new_order.id,
            dish_id=dish.id,
            quantity=item.quantity,
            price=row_price,
        )
        db.add(order_item)

        new_order.total_price = current_total
        await db.commit()
        await db.refresh(new_order)

        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == new_order.id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


# !!!!!!!! повторить і зрозуміть як все працює
@router.get("/orders", response_model=List[OrderResponse])
async def get_my_order(
    db: SessionDep, user_token=Depends(security.access_token_required)
):
    user_id = int(
        user_token.sub
    )  # У стандарті JWT (JSON Web Token) поле sub (subject) зазвичай зберігає ID користувача.
    # Але в токені це завжди рядок (текст).int(...): Ми перетворюємо текст "5" у число 5
    query = (
        select(OrderModel)
        .options(
            selectinload(OrderModel.items)
        )  # підтягни список товарів (items) для кожного замовлення".
        .where(
            OrderModel.user_id == user_id
        )  # Дай замовлення ТІЛЬКИ ті, де власник (user_id) дорівнює нашому user_id
        # (якого ми дістали з токена)". Це гарантує, що Вася побачить тільки замовлення Васі,
    )
    result = await db.execute(query)
    return result.scalars().all()
