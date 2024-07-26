from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from .room import Room
from .user import User
from .card import Card, CardRoomUserLinkTable


class BaseRoomUser(SQLModel):
    points: int = Field(default=0)

    user_id: int = Field(foreign_key="user.id")
    room_id: int = Field(foreign_key="room.id")


class RoomUser(BaseRoomUser, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)

    user: User = Relationship(back_populates="room_users")
    room: Room = Relationship(back_populates="players")
    cards: list[Card] = Relationship(
        back_populates="room_users", link_model=CardRoomUserLinkTable
    )


class ReadRoomUser(BaseRoomUser):
    id: int
