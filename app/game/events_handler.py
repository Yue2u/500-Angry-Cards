import asyncio
from sqlalchemy.orm import Session
import json
from nats.aio.client import Client as NATS

from app.cruds.room_user import get_room_user_by_id, delete_room_users
from app.models.room import Room
from app.models.room_user import RoomUser
from app.models.card import Card, CardBox


class EventsHandler:
    def __init__(self, db: Session, room: Room, cardbox: CardBox, nats: NATS):
        self.db = db
        self.nats = nats
        self.room = room
        self.question_cards = list(filter(lambda card: card.type == 0, cardbox.cards))
        self.answer_cards = list(filter(lambda card: card.type == 1, cardbox.cards))

        self.current_questioner_idx = 0
        self.answers = dict()

        self.last_answer_card_id = 0
        self.last_question_card_id = 0

        self.server_events = [
            "get_answers",
            "next_round",
            "start_game",
            "get_new_cards",
            "put_answer",
        ]
        self.user_events = ["end_game", "put_answer", "set_round_winner", "start_game"]
        self.user_event_handler = {
            "end_game": self.handle_end_game,
            "put_answer": self.handle_put_answer,
            "set_round_winner": self.handle_set_round_winner,
            "start_game": self.handle_start_game,
        }

    async def publish(self, data: dict):
        await self.nats.publish(f"room_{self.room.id}", json.dumps(data).encode())

    async def handle_user_event(self, event: dict):
        await self.refresh_data()
        handler = self.user_event_handler[event["name"]]
        await handler(event)

    async def handle_set_round_winner(self, event: dict):
        sender = await self.get_player_info(event["from"])
        if self.room.players.index(sender) != self.current_questioner_idx:
            print("Player", sender, "tryed to set round winner not being questioner")
            return

        data = event["data"]
        winner_id = data["winner_id"]

        winner = await self.set_round_winner(winner_id)
        await self.next_round()

        await self.publish(
            {
                "name": "set_round_winner",
                "data": {"winner_id": winner_id, "winner": winner.model_dump()},
                "to": "any",
                "from": "server",
            }
        )
        await self.publish(
            {
                "name": "next_round",
                "data": {
                    "questioner": self.room.players[
                        self.current_questioner_idx
                    ].model_dump(),
                    "question_card": self.__choose_question_cards(),
                },
                "to": "any",
                "from": "server",
            }
        )

        async def take_card_and_publish(player_id: int):
            cards = await self.get_new_cards(player_id)
            await self.publish(
                {
                    "name": "get_new_cards",
                    "data": {"cards": [card.model_dump() for card in cards]},
                    "to": player_id,
                    "from": "server",
                }
            )

        await asyncio.gather(
            *[take_card_and_publish(player.id) for player in self.room.players]
        )

    async def handle_put_answer(self, event: dict):
        questioner = await self.get_current_questioner()
        if event["from"] == questioner.id:
            print("Questioner", questioner, "tried to send an answer")
            return

        data = event["data"]
        player_id = data["player_id"]
        card = Card(**data["card"])

        await self.put_answer(player_id, card)
        if len(self.answers) == len(self.room.players):
            await self.publish(
                {
                    "name": "get_answers",
                    "to": self.room.players[self.current_questioner_idx].id,
                    "data": {"answers": await self.get_answers()},
                    "from": "server",
                }
            )
        await self.publish(
            {
                "name": "put_answer",
                "to": "any",
                "data": {"player": await self.get_player_info(player_id).model_dump()},
                "from": "server",
            }
        )

    async def handle_end_game(self, event: dict):
        winner = max(self.room.players, lambda p: p.points)
        await self.end_game()
        await self.publish(
            {
                "name": "game_finished",
                "data": {"winner": winner.model_dump()},
                "to": "any",
                "from": "server",
            }
        )

    async def handle_start_game(self, event: dict):
        await self.start_game()
        await self.publish(
            {"name": "start_game", "data": {}, "to": "any", "from": "server"}
        )

        async def take_card_and_publish(player_id: int):
            cards = await self.get_new_cards(player_id, n=10)
            await self.publish(
                {
                    "name": "get_new_cards",
                    "data": {"cards": [card.model_dump() for card in cards]},
                    "to": player_id,
                    "from": "server",
                }
            )

        await asyncio.gather(
            *[take_card_and_publish(player.id) for player in self.room.players]
        )

        await self.publish(
            {
                "name": "next_round",
                "data": {
                    "questioner": self.room.players[
                        self.current_questioner_idx
                    ].model_dump(),
                    "question_card": self.__choose_question_cards().model_dump(),
                },
                "to": "any",
                "from": "server",
            }
        )

    async def get_answers(self):
        """Get answers list"""
        return self.answers

    async def next_round(self):
        """Start new round: change questioner"""
        self.answers = dict()
        self.current_questioner_idx = (self.current_questioner_idx + 1) % len(
            self.room.players
        )

    async def refresh_data(self):
        await asyncio.gather(self.db.refresh(self.room, Room.refresh_list()))

    async def start_game(self):
        """Change game status from STARTING to IN_PROCESS"""
        await self.db.refresh(self.room)
        self.room.start_game()
        self.db.add(self.room)
        await self.db.commit()
        await self.db.refresh(self.room)
        return self.room

    async def end_game(self):
        """Change game status from IN_PROCESS to FINISHED"""
        await self.db.refresh(self.room)
        self.room.end_game()
        self.db.add(self.room)
        await delete_room_users(self.db, self.room.players)
        await self.db.delete(self.room)
        await self.db.commit()
        await self.db.refresh(self.room)
        return self.room

    async def put_answer(self, player_id: int, card: Card):
        """Put user's answer in current
        round and delete card from user's hand"""
        player = await get_room_user_by_id(self.db, player_id)
        player.cards.remove(card)
        self.db.add(player)
        await self.db.commit()
        self.answers[player_id] = card

    async def set_round_winner(self, winner_id: int):
        """Set round winner and start next_round"""
        winner: RoomUser = await get_room_user_by_id(self.db, winner_id)
        if not winner:
            return None

        winner.points += 1
        self.db.add(winner)
        await self.db.commit()
        await self.db.refresh(winner)
        return winner

    async def get_current_questioner(self):
        """Get current questioner"""
        questioner = self.room.players[self.current_questioner_idx]
        await self.db.refresh(questioner)
        return questioner

    async def get_player_info(self, player_id: int):
        """Get info about player"""
        player = await get_room_user_by_id(self.db, player_id)
        return player

    def __choose_question_cards(self):
        card = self.question_cards[self.last_question_card_id]
        self.last_question_card_id = (self.last_question_card_id + 1) % len(
            self.question_cards
        )
        return card

    def __choose_answer_cards(self, exclude: list[Card], n: int = 1):
        result = []

        i = 0
        walks = 0
        while len(result) != n and walks < 2:
            if i == len(self.answer_cards):
                walks += 1
                i = 0
            card = self.answer_cards[i]
            if card not in exclude and card.type == 1:  # answer cards
                result.append(card)

            i += 1

        self.last_answer_card_id = i + 1
        return result

    async def get_new_cards(self, player_id: int, n: int = 1):
        """Get new card for player"""
        player = await get_room_user_by_id(self.db, player_id)
        new_cards = self.__choose_answer_cards(player.cards, n)
        for card in new_cards:
            player.cards.append(card)
        self.db.add(player)
        await self.db.commit()

        print(new_cards)
        return new_cards
