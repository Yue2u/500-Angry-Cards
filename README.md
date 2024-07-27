# 500 Angry cards
This is first alpha 0.0.1 version of game (I'm 99% sure it doesnt work normally). There still a lot of things to do about game host function.

## How to play

1. Create user and return his id
2. Create room with this user and generate joining code/by id
3. Wait for users to connect through websocket
4. Choose card stack and start game
5. Handle events through websocket

## Websocket events
### Server events:
1. "get_answers" - send answers to questioner
2. "next_round" - start next round (choose new questioner and give everyone a card)
3. "start_game" - notify everyine that game started (and give 10 cards to everyone)
4. "get_new_cards" - give users new answer cards
5. "put_answer" - notify everyone that player put answer
6. "User joined" - notify that player joined

### User events (they trigger server events):
1. "end_game" - end game (notify everyone about winner)
2. "put_answer" - send answer to question
3. "set_round_winner" - set winner of round by answers
4. "start_game" - trigger server "start_game" event

# Stack
Docker compose, Fastapi, postgresql (through sqlmodel orm), websockets, NATS
