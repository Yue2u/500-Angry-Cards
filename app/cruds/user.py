from sqlmodel import select, delete
from sqlalchemy.orm import Session, selectinload

from app.models.user import User, CreateUser, UpdateUser
from .utils import generate_nickname


async def update_or_create_user(db: Session, user_ip: str, nickname: str):
    nickname = nickname if nickname else generate_nickname()
    stmt = select(User).where(User.ip == user_ip)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is not None:
        nickname = user.nickname if user.nickname else nickname
        user.nickname = nickname
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    user = User(ip=user_ip, nickname=nickname, victories=0)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: Session, user_id: int):
    stmt = select(User).options(User.rooms).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_user(db: Session, user: CreateUser):
    new_user = User.model_validate(user)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user, User.refresh_list())
    return new_user


async def update_user(db: Session, user_id: int, user: UpdateUser):
    db_user = await get_user_by_id(db, user_id)
    if not user:
        return None

    db_user.sqlmodel_update(user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user, User.refresh_list())
    return db_user
