from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_session
from app.cruds.room import delete_rooms

from .routers.game import router as game_router
from .routers.room import router as room_router
from .routers.card import router as card_router

fastapi_app = FastAPI(
    title="500 Angry Cards",
)

fastapi_app.include_router(game_router)
fastapi_app.include_router(room_router, prefix="/api")
fastapi_app.include_router(card_router, prefix="/api")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
    allow_credentials=True,
)


@fastapi_app.on_event("shutdown")
async def on_shutdown():
    async with get_session() as db:
        await delete_rooms(db)
