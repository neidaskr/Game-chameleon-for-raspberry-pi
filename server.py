import random
sid_map = {}

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
    if username not in players:
        players.append(username)
        sid_map[username] = sid  # Save their socket ID
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
        # Game start
        word_list = ["Pineapple", "Rocket", "Pencil", "Submarine", "Volcano"]
        secret_word = random.choice(word_list)
        chameleon = random.choice(players)

        for player in players:
            if player == chameleon:
                socketio.emit('game_data', {'role': 'player', 'word': secret_word}, to=sid_map[player])
            else:
                socketio.emit('game_data', {'role': 'chameleon'}, to=sid_map[player])



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
