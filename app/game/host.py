from typing import Annotated
from fastapi import Depends
import asyncio
from sqlalchemy.orm import Session
import json
import time

from app.nats import get_nats
from app.models.room import GameState
from app.cruds.room import get_room_by_id
from app.cruds.card import get_cardbox_by_id
from .events_handler import EventsHandler


async def host_game(db: Session, room_id: int, cardbox_id: int):
    cb, room = await asyncio.gather(
        get_cardbox_by_id(db, cardbox_id), get_room_by_id(db, room_id)
    )
    if not cb:
        print("No such cardbox with id", cardbox_id)
        if room:
            await db.delete(room)
            await db.commit()
            return
    if not room:
        print("No room with id", room_id)
        return

    async for nats in get_nats():
        events_handler = EventsHandler(db, room, cb, nats)

        wait_until = time.time() + 60 * 15

        sub = await nats.subscribe(f"room_{room_id}")
        while events_handler.room.game_status != GameState.FINISHED and (
            events_handler.room.players or time.time() < wait_until
        ):
            await asyncio.sleep(0.5)
            await events_handler.refresh_data()
            print(
                f"Game {events_handler.room.id}",
                "is running, players:",
                events_handler.room.players,
            )
            message = await sub.next_msg(timeout=900)
            print("Server got message", message.data.decode())
            if message:
                event = json.loads(message.data.decode())
                if (
                    event["name"] in events_handler.user_events
                    and event["from"] != "server"
                ):
                    await events_handler.handle_user_event(event)

        print("Closing room cause no players here")
        await sub.unsubscribe()
        await events_handler.end_game()
