from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.room_user import RoomUser
from app.cruds.room import get_room_by_code


async def get_room_user_by_id(db: Session, user_id: int):
    stmt = (
        select(RoomUser)
        .options(selectinload(RoomUser.room), selectinload(RoomUser.cards))
        .where(RoomUser.id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_room_user_by_user_id(db: Session, user_id: int):
    stmt = (
        select(RoomUser)
        .options(selectinload(RoomUser.room), selectinload(RoomUser.cards))
        .where(RoomUser.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_or_create_room_user(db: Session, user_id: int, room_code: int):
    user = await get_room_user_by_user_id(db, user_id)
    room = await get_room_by_code(db, room_code)
    if not user:
        db_user = RoomUser(user_id=user_id, room_id=room.id)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user, ["user", "room"])
        return db_user
    user.room_id = room.id
    await db.commit()
    await db.refresh(user, ["user", "room"])
    return user


async def delete_room_users(db: Session, room_user: list[RoomUser]):
    await db.delete(room_user)
    await db.commit()
