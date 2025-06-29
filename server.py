import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

players = []
ready_clients = set()
sid_map = {}
player_data = {}
votes = {}
chameleon = None
secret_word = None

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    sid = request.sid
    name = data['name']

    if name in players:
        emit('join_error', {'message': 'Name already taken'})
        return

    player_data[sid] = name
    sid_map[name] = sid
    players.append(name)
    print(f"{name} joined.")
    emit('player_list', {'players': players}, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    name = player_data.get(sid)
    if name:
        players.remove(name)
        sid_map.pop(name, None)
        player_data.pop(sid, None)
    emit('player_list', {'players': players}, broadcast=True)

@socketio.on("start_game")
def handle_start_game():
    global chameleon, secret_word
    if len(players) < 2:
        emit("join_error", {"message": "Need at least 2 players to start"})
        return

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

@socketio.on('client_ready')
def handle_client_ready():
    ready_clients.add(request.sid)
    if len(ready_clients) == len(players):
        socketio.emit("start_timer")

@socketio.on("request_player_list")
def send_players():
    emit("player_list", {"players": players})

@socketio.on("submit_vote")
def receive_vote(data):
    voter_sid = request.sid
    voter_name = player_data.get(voter_sid)
    voted = data["vote"]
    votes[voter_name] = voted
    print(f"{voter_name} voted for {voted}")

    if len(votes) == len(players):
        socketio.emit("voting_result", {
            "votes": votes,
            "chameleon": chameleon
        })
        reset_game()

def reset_game():
    global ready_clients, votes, chameleon, secret_word
    ready_clients.clear()
    votes.clear()
    chameleon = None
    secret_word = None

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
