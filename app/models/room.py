from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class GameState(Enum):
    STARTING = 0
    IN_PROCESS = 1
    FINISHED = 2


class Room(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    game_status: int = Field(default=GameState.STARTING.value)
    code: str = Field(max_length=6)
    players: list["RoomUser"] = Relationship(back_populates="room", cascade_delete=True)

    @staticmethod
    def refresh_list():
        return ["players"]

    def start_game(self):
        self.game_status = GameState.IN_PROCESS.value

    def end_game(self):
        self.game_status = GameState.FINISHED.value


class ReadRoom(SQLModel):
    class ReadRoomUser(SQLModel):
        id: int
        points: int

        user_id: int
        room_id: int

    id: Optional[int]
    game_status: int
    code: str
    players: list[ReadRoomUser] = []
