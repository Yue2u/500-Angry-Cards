from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from app.db import get_session
from app.models.card import (
    ReadCard,
    CreateCard,
    UpdateCard,
    ReadCardBox,
    ReadCardBoxWithCards,
    CreateCardBox,
)
from app.cruds.card import (
    create_card,
    create_cardbox,
    get_card_by_id,
    get_cardbox_by_id,
    add_card_to_cardbox,
    update_card,
    list_cardboxes,
    list_cards,
)


router = APIRouter(tags=["cards"])


@router.get("/cards", response_model=list[ReadCard])
async def get_list_of_cards(db: Annotated[Session, Depends(get_session)]):
    result = await list_cards(db)
    return result


@router.get("/cardboxes", response_model=list[ReadCardBox])
async def get_list_of_cardboxes(db: Annotated[Session, Depends(get_session)]):
    result = await list_cardboxes(db)
    return result


@router.get("/cards/{card_id}", response_model=ReadCard)
async def get_card_by_id_api(
    db: Annotated[Session, Depends(get_session)], card_id: int
):
    card = await get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return card


@router.post("/cards", response_model=ReadCard)
async def create_card_api(
    db: Annotated[Session, Depends(get_session)], card: CreateCard
):
    new_card = await create_card(db, card)
    if not new_card:
        raise HTTPException(status_code=400, detail="Wrong card format")

    return new_card


@router.patch("/cards/{card_id}", response_model=ReadCard)
async def update_card_api(
    db: Annotated[Session, Depends(get_session)], card_id: int, card: UpdateCard
):
    updated = await update_card(db, card_id, card)
    if not updated:
        raise HTTPException(status_code=404, detail="Card not found")

    return updated


@router.delete("/cards/{card_id}", response_model=ReadCard)
async def delete_card_api(db: Annotated[Session, Depends(get_session)], card_id: int):
    card = await get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    await db.delete(card)
    await db.commit()
    return card


@router.get("/cardboxes/{cb_id}", response_model=ReadCardBoxWithCards)
async def get_cardbox_by_id_api(
    db: Annotated[Session, Depends(get_session)], cb_id: int
):
    cb = await get_cardbox_by_id(db, cb_id)
    if not cb:
        raise HTTPException(status_code=404, detail="Cardbox not found")

    return cb


@router.post("/cardboxes", response_model=ReadCardBox)
async def create_cardbox_api(
    db: Annotated[Session, Depends(get_session)], card: CreateCardBox
):
    new_cb = await create_cardbox(db, card)
    if not new_cb:
        raise HTTPException(status_code=400, detail="Wrong cardbox format")

    return new_cb


@router.post(
    "/cardboxes/{cb_id}/add_card_to_cardbox/{card_id}",
    response_model=ReadCardBoxWithCards,
)
async def add_card_to_cardbox_api(
    db: Annotated[Session, Depends(get_session)], cb_id: int, card_id: int
):
    cb = await add_card_to_cardbox(db, card_id, cb_id)
    if not cb:
        raise HTTPException(status_code=400, detail="Something went wrong...")
    return cb
