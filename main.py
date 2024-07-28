import json
import websockets
import asyncio
import httpx


BASE_URL = "500-angry-production.up.railway.app"


async def main():
    cards = []
    my_id = 1

    # resp = httpx.post(f"https://{BASE_URL}/api/room/create_room?cardbox_id=1")
    # d = resp.json()
    # print('d')
    # code = d['code']

    code = "JUFXIX"
    async with websockets.connect(
        f"wss://{BASE_URL}/ws/connect_nats?nickname=Oleg&room_code={code}"
    ) as ws:
        data = {"name": "end_game", "from": my_id, "data": {}, "to": "any"}
        await ws.send(json.dumps(data))
        async for msg in ws:
            event = json.loads(msg)
            if event["name"] == "user_joined":
                print("User", event["data"]["user_nickname"], "joined")
                my_id = event["data"]["user_id"]
            elif event["name"] == "start_game":
                print("Game started")
            elif event["name"] == "get_new_cards":
                print("Got cards", event["data"]["cards"])
                cards += event["data"]["cards"]
            elif event["name"] == "next_round":
                print(
                    "Next round started!\n",
                    "Questioner is ",
                    event["data"]["questioner"],
                    "\n",
                    "Question is ",
                    event["data"]["question_card"],
                    sep="",
                )
                print("My cards are", cards, "choose idx from 0 to", len(cards))
                idx = int(input())
                card = cards.pop(idx)
                await ws.send(
                    json.dumps(
                        {
                            "name": "put_answer",
                            "data": {"player_id": my_id, "card": card},
                            "from": my_id,
                            "to": "server",
                        }
                    )
                )
            elif event["name"] == "put_answer":
                print("User", event["data"]["player"], "got a card")
            elif event["name"] == "get_answers":
                print("Answers are", event["data"]["answers"])


asyncio.run(main())
# for i in range(50):
#     resp = httpx.post(f"https://{BASE_URL}/api/cards?cardbox_id=1", json={"type": 1, "content": f"Answer {i}"})
#     print(resp.json() if resp.status_code == 200 else resp)
#     data = resp.json()
#     # httpx.post(f"http://backend.localhost/api/cardboxes/1/add_card_to_cardbox/{data.get('id')}")

# for i in range(50):
#     resp = httpx.post(f"https://{BASE_URL}/api/cards?cardbox_id=1", json={"type": 0, "content": f"Question {i}"})
#     print(resp.json() if resp.status_code == 200 else resp)
#     data = resp.json()
#     # httpx.post(f"http://backend.localhost/api/cardboxes/1/add_card_to_cardbox/{data.get('id')}")
