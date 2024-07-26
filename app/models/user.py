from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from .room import Room


class BaseUser(SQLModel):
    ip: str
    nickname: str = Field(max_length=20)
    victories: int = Field(default=0)


class User(BaseUser, table=True):
    id: Optional[int] = Field(primary_key=True)

    room_users: list["RoomUser"] = Relationship(back_populates="user")

    @staticmethod
    def refresh_list():
        return ["rooms"]


class ReadUser(BaseUser):
    id: Optional[int]
    nickname: str
    victories: int


class ReadUserWithRoom(ReadUser):
    rooms: list[Room] = []
    room_users: list["RoomUser"] = []


class CreateUser(BaseUser):
    pass


class UpdateUser(SQLModel):
    nickname: str
