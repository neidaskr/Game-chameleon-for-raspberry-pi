# server.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

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
        emit('player_list', {'players': players}, broadcast=True)

@socketio.on('player_ready')
def on_ready(data):
    ready_players.add(data['name'])
    if len(ready_players) == len(players):
        emit('start_game', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
