from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from passlib.context import CryptContext
from authx import AuthX, AuthXConfig
from datetime import timedelta

from database.db import SessionDep
from models.models import UserModel
from schemas.schemas import UserLogin, UserResponse

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    print("PASSWORD VALUE:", password)
    print("PASSWORD TYPE:", type(password))
    print("PASSWORD LENGTH:", len(password))
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY" # У реальному проекті це має бути складний код
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1) # Токен живе 1 день
config.JWT_TOKEN_LOCATION = ["headers"] # Поки що тільки заголовки (найстабільніше)

security = AuthX(config)

@router.post("/register", response_model=UserResponse)
async def register(user_data:UserLogin, db: SessionDep):
    query = select(UserModel).where(UserModel.username == user_data.username)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already registered")

    hashed_pass = get_password_hash(user_data.password)

    new_user = UserModel(
        username=user_data.username,
        hashed_password=hashed_pass,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login")
async def login(creds: UserLogin, db: SessionDep):
    query = select(UserModel).where(UserModel.username == creds.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = security.create_access_token(uid=str(user.id))

    return {"token": token}
