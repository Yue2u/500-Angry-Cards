# How to play

1. Create user and return his id
2. Create room with this user and generate joining code/by id
3. Wait for users to connect through websocket
4. Choose card stack and start game with HTTP request and choose fir
5. Handle events through websocket

# Websocket events
server events:
1. New round (change questioner and give him a card) "next_round"
2. Get new card "get_new_card"
3. Give list of answers "get_answers"
4. Give card to round winner?
5. Notify about end of the game and send a winner "end_game" returning value

User events (they trigger server events):
1. Choose winner card "set_round_winner"
2. Send card to questioner "put_answer"
3. End the game "end_game"
