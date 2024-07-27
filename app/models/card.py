from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class CardType(Enum):
    QUESTION = 0
    ANSWER = 1


class CardCardBoxLinkTable(SQLModel, table=True):
    card_id: int | None = Field(default=None, foreign_key="card.id", primary_key=True)
    cardbox_id: int | None = Field(
        default=None, foreign_key="cardbox.id", primary_key=True
    )


class CardRoomUserLinkTable(SQLModel, table=True):
    card_id: int | None = Field(default=None, foreign_key="card.id", primary_key=True)
    room_user_id: int | None = Field(
        default=None, foreign_key="roomuser.id", primary_key=True, ondelete="CASCADE"
    )


class Card(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    type: int
    content: str = Field(max_length=512)

    card_boxes: list["CardBox"] = Relationship(
        back_populates="cards", link_model=CardCardBoxLinkTable
    )
    room_users: list["RoomUser"] = Relationship(
        back_populates="cards", link_model=CardRoomUserLinkTable
    )


class ReadCard(SQLModel):
    id: int
    type: int
    content: str


class CreateCard(SQLModel):
    type: int
    content: str


class UpdateCard(SQLModel):
    type: int | None = None
    content: int | None = None


class CardBox(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str = Field(max_length=128)

    cards: list[Card] = Relationship(
        back_populates="card_boxes", link_model=CardCardBoxLinkTable
    )

    @staticmethod
    def refresh_list():
        return ["cards"]


class ReadCardBox(SQLModel):
    id: Optional[int]
    title: str


class ReadCardBoxWithCards(SQLModel):
    id: Optional[int]
    title: str

    cards: list[ReadCard] = []


class CreateCardBox(SQLModel):
    title: str
