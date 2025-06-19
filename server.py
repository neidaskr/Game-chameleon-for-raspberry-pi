# server.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')


players = []
ready_players = set()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['name']
    if username not in players:
        players.append(username)
    # Reset ready_players every time someone joins
    ready_players.clear()
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
    if len(ready_players) == len(players) and len(players) > 0:
        emit('start_game', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
