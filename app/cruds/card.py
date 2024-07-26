import asyncio
from sqlalchemy import select, not_, and_
from sqlalchemy.orm import Session, selectinload

from app.models.card import Card, CardBox, CreateCard, CreateCardBox, UpdateCard


async def list_cards(db: Session):
    stmt = select(Card)
    result = await db.execute(stmt)
    return result.scalars().all()


async def list_cardboxes(db: Session):
    stmt = select(CardBox)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_card_by_id(db: Session, card_id: int):
    stmt = select(Card).options(selectinload(Card.card_boxes)).where(Card.id == card_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def update_card(db: Session, card_id: int, card: UpdateCard):
    db_card: Card = await get_card_by_id(db, card_id)
    if not db_card:
        return None
    db_card.sqlmodel_update(card)
    db.add(db_card)
    await db.commit()
    await db.refresh(db_card)
    return db_card


async def get_cardbox_by_id(db: Session, cb_id: int):
    stmt = (
        select(CardBox).options(selectinload(CardBox.cards)).where(CardBox.id == cb_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_card(db: Session, card: CreateCard):
    db_card = Card.model_validate(card)
    db.add(db_card)
    await db.commit()
    await db.refresh(db_card)
    return db_card


async def create_cardbox(db: Session, cb: CreateCardBox):
    db_cb = CardBox.model_validate(cb)
    db.add(db_cb)
    await db.commit()
    await db.refresh(db_cb, CardBox.refresh_list())
    return db_cb


async def add_card_to_cardbox(db: Session, card_id: int, cb_id: int):
    card, cb = await asyncio.gather(
        get_card_by_id(db, card_id), get_cardbox_by_id(db, cb_id)
    )

    cb.cards.append(card)
    db.add(cb)
    await db.commit()
    await db.refresh(cb, CardBox.refresh_list())
    return cb


async def choose_cards(
    db: Session, cardbox_id: int, exclude: list[Card], offset: int = 0, limit: int = 1
):
    stmt = (
        select(Card)
        .where(
            and_(
                not_(Card.id.in_([card.id for card in exclude])),
                Card.cardbox_id == cardbox_id,
            )
        )
        .order_by(Card.id)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
