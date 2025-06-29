import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

zaidejai = []
sid_zemelapis = {}
zaidejo_duomenys = {}
balsai = {}
pasiruose = set()
chameleonas = None
slaptas_zodis = None

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    sid = request.sid
    vardas = data['name']

    if vardas in zaidejai:
        emit('join_error', {'message': 'Toks vardas jau užimtas'})
        return

    zaidejo_duomenys[sid] = vardas
    sid_zemelapis[vardas] = sid
    zaidejai.append(vardas)
    print(f"{vardas} prisijungė prie žaidimo.")
    emit('player_list', {'players': zaidejai}, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    vardas = zaidejo_duomenys.get(sid)
    if vardas:
        zaidejai.remove(vardas)
        sid_zemelapis.pop(vardas, None)
        zaidejo_duomenys.pop(sid, None)
        pasiruose.discard(sid)
    emit('player_list', {'players': zaidejai}, broadcast=True)

@socketio.on("start_game")
def start_game():
    global chameleonas, slaptas_zodis
    if len(zaidejai) < 2:
        emit("join_error", {"message": "Reikia bent 2 žaidėjų"})
        return

    zodziu_sarasas = ["Ananasas", "Raketa", "Pieštukas", "Povandeninis laivas", "Ugnikalnis"]
    slaptas_zodis = random.choice(zodziu_sarasas)
    chameleonas = random.choice(zaidejai)
    print(f"[Žaidimo pradžia] Žodis: {slaptas_zodis}, Chameleonas: {chameleonas}")

    for zaidejas in zaidejai:
        sid = sid_zemelapis[zaidejas]
        if zaidejas == chameleonas:
            socketio.emit("game_data", {"role": "chameleon"}, to=sid)
        else:
            socketio.emit("game_data", {"role": "player", "word": slaptas_zodis}, to=sid)

@socketio.on("client_ready")
def client_ready():
    sid = request.sid
    pasiruose.add(sid)
    if len(pasiruose) == len(zaidejai):
        socketio.emit("start_timer")

@socketio.on("request_player_list")
def send_players():
    socketio.emit("voting_phase", {"players": zaidejai})

@socketio.on("submit_vote")
def submit_vote(data):
    voter_sid = request.sid
    balsaves = zaidejo_duomenys.get(voter_sid)
    balsas_uz = data["vote"]
    balsai[balsaves] = balsas_uz
    print(f"{balsaves} balsavo už {balsas_uz}")

    if len(balsai) == len(zaidejai):
        socketio.emit("voting_result", {
            "votes": balsai,
            "chameleon": chameleonas
        })
        reset_game()

def reset_game():
    global balsai, chameleonas, slaptas_zodis, pasiruose
    balsai.clear()
    chameleonas = None
    slaptas_zodis = None
    pasiruose.clear()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
