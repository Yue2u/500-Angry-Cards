import json
from websockets.sync.client import connect
import httpx


with connect(
    "ws://backend.localhost/ws/connect_nats?nickname=Oleg&room_code=PVUNQO"
) as ws:
    data = {"name": "start_game", "from": 1, "data": {}, "to": "any"}
    ws.send(json.dumps(data))
    while True:
        msg = ws.recv()
        event = json.loads(msg)
        if event["name"] == "user_joined":
            print("User", event["data"]["user_nickname"], "joined")
        elif event["name"] == "start_game":
            print("Game started")
        elif event["name"] == "get_new_cards":
            print("Got cards", event["data"]["cards"])
        elif event["name"] == "next_round":
            print(
                "Next round started!\n",
                "Questioner is",
                event["data"]["questioner"],
                "\n",
                "Question is",
                event["data"]["question_card"],
                sep="",
            )

# for i in range(50):
#     resp = httpx.post("http://backend.localhost/api/cards", json={"type": 1, "content": f"Answer {i}"})
#     print(resp)
#     data = resp.json()
#     httpx.post(f"http://backend.localhost/api/cardboxes/1/add_card_to_cardbox/{data.get('id')}")
