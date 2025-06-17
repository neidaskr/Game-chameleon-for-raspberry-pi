from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

# Game state
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    game_id = data['game_id']
    
    if game_id not in games:
        games[game_id] = {'players': [], 'word': '', 'chameleon': '', 'clues': [], 'votes': {}}
    
    games[game_id]['players'].append(username)
    session['username'] = username
    session['game_id'] = game_id
    
    emit('player_joined', {'username': username}, broadcast=True)

@app.route('/game')
def game():
    return render_template('game.html')

@socketio.on('start_game')
def start_game(data):
    game_id = data['game_id']
    words = ['apple', 'banana', 'cherry']  # Example word list
    word = random.choice(words)
    
    games[game_id]['word'] = word
    chameleon_index = random.randint(0, len(games[game_id]['players']) - 1)
    games[game_id]['chameleon'] = games[game_id]['players'][chameleon_index]
    
    emit('game_started', {'word': word, 'chameleon': games[game_id]['chameleon']}, broadcast=True)

@socketio.on('submit_clue')
def submit_clue(data):
    game_id = session['game_id']
    clue = data['clue']
    username = session['username']
    
    games[game_id]['clues'].append({'username': username, 'clue': clue})
    emit('new_clue', {'username': username, 'clue': clue}, broadcast=True)

@socketio.on('vote')
def vote(data):
    game_id = session['game_id']
    voted_username = data['voted_username']
    username = session['username']
    
    games[game_id]['votes'][username] = voted_username
    emit('new_vote', {'voted_username': voted_username}, broadcast=True)

@socketio.on('end_game')
def end_game(data):
    game_id = session['game_id']
    chameleon = games[game_id]['chameleon']
    votes = games[game_id]['votes']
    
    # Determine the result
    # Logic to determine if the chameleon was guessed correctly
    emit('game_ended', {'chameleon': chameleon, 'votes': votes}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)