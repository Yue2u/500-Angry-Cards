from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
import json
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

from app.db import get_session
from app.redis import redis
from app.nats import get_nats
from app.cruds.user import update_or_create_user
from app.cruds.room_user import get_room_user_by_user_id, get_or_create_room_user

router = APIRouter()


# TODO: clear room_user on connect, delete all rooms and room_users on shutdown
@router.websocket("/ws/connect")
async def connect_to_game(
    websocket: WebSocket,
    db: Annotated[Session, Depends(get_session)],
    nickname: str,
    room_code: str,
):
    print(nickname, room_code)
    user_ip = websocket.headers.get("X-Forwarded-For")
    user = await update_or_create_user(db, user_ip=user_ip, nickname=nickname)
    room_user = await get_or_create_room_user(db, user.id, room_code)
    print(room_user.room)

    await websocket.accept()
    async with redis.pubsub() as p:
        channel = f"room_{room_user.room_id}"

        async def message_callback(message):
            print("Message sent to user", message)
            event = json.loads(message["data"].decode("utf-8"))
            if event["to"] in (room_user.id, "any"):
                await websocket.send_json(event)

        await p.subscribe(**{channel: message_callback})
        await redis.publish(
            channel,
            json.dumps(
                {
                    "name": "user_joined",
                    "data": {"user_id": room_user.id, "user_nickname": user.nickname},
                    "to": "any",
                    "from": "user",
                }
            ),
        )

        if not p:
            await websocket.close()
            return
        try:
            while True:
                ws_message = await websocket.receive_text()
                print("Msg from user", ws_message)
                await redis.publish(channel, ws_message)

        except WebSocketDisconnect:
            await redis.publish(
                channel,
                json.dumps(
                    {
                        "name": "user_disconnected",
                        "data": {
                            "user_id": room_user.id,
                            "user_nickname": user.nickname,
                        },
                        "to": "any",
                        "from": "user",
                    }
                ),
            )
            await p.unsubscribe()


# TODO: clear room_user on connect, delete all rooms and room_users on shutdown
@router.websocket("/ws/connect_nats")
async def connect_to_game_w_nats(
    websocket: WebSocket,
    db: Annotated[Session, Depends(get_session)],
    nats: Annotated[NATS, Depends(get_nats)],
    nickname: str,
    room_code: str,
):
    print(nickname, room_code)
    user_ip = websocket.headers.get("X-Forwarded-For")
    user = await update_or_create_user(db, user_ip=user_ip, nickname=nickname)
    room_user = await get_or_create_room_user(db, user.id, room_code)
    print(room_user.room)

    await websocket.accept()
    channel = f"room_{room_user.room_id}"

    async def message_callback(message: Msg):
        print("Message sent to user", message.data.decode())
        event = json.loads(message.data.decode())
        if event["to"] in (room_user.id, "any") and event["from"] != room_user.id:
            await websocket.send_json(event)

    await nats.subscribe(channel, cb=message_callback)
    await nats.publish(
        channel,
        json.dumps(
            {
                "name": "user_joined",
                "data": {"user_id": room_user.id, "user_nickname": user.nickname},
                "to": "any",
                "from": "user",
            }
        ).encode(),
    )

    try:
        while True:
            ws_message = await websocket.receive_text()
            print("Msg from user", ws_message)
            await nats.publish(channel, ws_message.encode())

    except WebSocketDisconnect:
        await nats.publish(
            channel,
            json.dumps(
                {
                    "name": "user_disconnected",
                    "data": {"user_id": room_user.id, "user_nickname": user.nickname},
                    "to": "any",
                    "from": "user",
                }
            ).encode(),
        )
