from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.game.host import host_game
from app.cruds.room import create_room, get_room_by_id
from app.models.room import ReadRoom


router = APIRouter(prefix="/room", tags=["room"])


@router.get("/{room_id}", response_model=ReadRoom)
async def get_room_api(db: Annotated[Session, Depends(get_session)], room_id: int):
    room = await get_room_by_id(db, room_id)
    return room


@router.post("/create_room", response_model=ReadRoom)
async def create_room_api(
    db: Annotated[Session, Depends(get_session)], bt: BackgroundTasks, cardbox_id: int
):
    new_room = await create_room(db)
    bt.add_task(host_game, db=db, room_id=new_room.id, cardbox_id=cardbox_id)
    return new_room
