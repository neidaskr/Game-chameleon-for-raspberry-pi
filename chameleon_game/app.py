import random
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

# Game state
games = {}

def generate_game_pin():
    return str(random.randint(1000, 9999))  # 4-digit PIN

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_game')
def new_game():
    game_id = generate_game_pin()
    games[game_id] = {'players': [], 'word': None, 'chameleon': None, 'clues': [], 'votes': {}, 'game_started': False}
    return render_template('index.html', game_id=game_id)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    game_id = data['game_id']

    if game_id not in games:
        emit('join_failed', {'message': 'Invalid game PIN'})
        return

    if username not in games[game_id]['players']:
        games[game_id]['players'].append(username)
        session['username'] = username
        session['game_id'] = game_id
        join_room(game_id)
        print(f"{username} has joined room {game_id}")
        emit('player_joined', {'players': games[game_id]['players']}, room=game_id)
    
    # Check if enough players have joined to enable the start button
    if len(games[game_id]['players']) >= 3 and not games[game_id]['game_started']:
        emit('enable_start_button', room=game_id)

@app.route('/game')
def game():
    return render_template('game.html')

@socketio.on('start_game')
def start_game():
    game_id = session['game_id']

    if len(games[game_id]['players']) < 3:
        emit('not_enough_players', room=game_id)
        return

    words = ['apple', 'banana', 'cherry']  # Example word list
    word = random.choice(words)

    games[game_id]['word'] = word
    chameleon_index = random.randint(0, len(games[game_id]['players']) - 1)
    games[game_id]['chameleon'] = games[game_id]['players'][chameleon_index]
    games[game_id]['game_started'] = True

    emit('game_started', {'word': word, 'chameleon': games[game_id]['chameleon']}, room=game_id)

@socketio.on('submit_clue')
def submit_clue(data):
    game_id = session['game_id']
    clue = data['clue']
    username = session['username']

    games[game_id]['clues'].append({'username': username, 'clue': clue})
    emit('new_clue', {'username': username, 'clue': clue}, room=game_id)

@socketio.on('vote')
def vote(data):
    game_id = session['game_id']
    voted_username = data['voted_username']
    username = session['username']

    games[game_id]['votes'][username] = voted_username
    emit('new_vote', {'voted_username': voted_username}, room=game_id)

@socketio.on('end_game')
def end_game(data):
    game_id = session['game_id']

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)