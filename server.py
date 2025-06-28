import random
sid_map = {}
votes = {}

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit



app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')


players = []
ready_players = set()

@app.route('/')
def index():
    return render_template('index.html')

sid_map = {}

@socketio.on('join')
def on_join(data):
    username = data['name']
    sid = request.sid

    if username in players:
        emit('join_error', {'message': 'Name already taken'})
        return

    players.append(username)
    sid_map[username] = sid
    emit('player_list', {'players': players}, broadcast=True)




@socketio.on('disconnect')
def on_disconnect():
    # Remove player from players and ready_players
    # Note: This requires tracking username by session, so for now, remove by sid if possible
    # But since we only have names, we can't reliably remove on disconnect
    pass  # For a robust solution, track players by sid and name
    emit('player_list', {'players': players}, broadcast=True)


@socketio.on('player_ready')
def on_ready(data):
    ready_players.add(data['name'])

    if len(ready_players) == len(players):
        # Only start game when everyone is ready
        word_list = ["Pineapple", "Rocket", "Pencil", "Submarine", "Volcano"]
        secret_word = random.choice(word_list)
        chameleon = random.choice(players)

        print(f"[Game Start] Word: {secret_word}, Chameleon: {chameleon}")

        for player in players:
            sid = sid_map[player]
            if player == chameleon:
                socketio.emit('game_data', {'role': 'chameleon'}, to=sid)
            else:
                socketio.emit('game_data', {'role': 'player', 'word': secret_word}, to=sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    
@socketio.on("request_player_list")
def send_players():
    emit("player_list", {"players": players})

@socketio.on("submit_vote")
def receive_vote(data):
    voter_sid = request.sid
    voter_name = None
    for name, sid in sid_map.items():
        if sid == voter_sid:
            voter_name = name
            break

    voted = data["vote"]
    votes[voter_name] = voted
    print(f"{voter_name} voted for {voted}")

    if len(votes) == len(players):
        # All players voted, announce result
        socketio.emit("voting_result", {"votes": votes})
