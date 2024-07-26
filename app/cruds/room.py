from sqlalchemy import select, delete
from sqlalchemy.orm import Session, selectinload

from app.models.room import Room
from .utils import generate_room_code


async def get_room_by_id(db: Session, room_id: int):
    stmt = select(Room).options(selectinload(Room.players)).where(Room.id == room_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_room_by_code(db: Session, room_code: str):
    stmt = (
        select(Room).options(selectinload(Room.players)).where(Room.code == room_code)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_room(db: Session):
    new_room = Room(code=generate_room_code())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room, Room.refresh_list())
    return new_room


async def delete_room(db: Session, room_id):
    stmt = delete(Room).where(Room.id == room_id)
    await db.execute(stmt)


async def delete_rooms(db: Session):
    stmt = delete(Room)
    await db.execute(stmt)
