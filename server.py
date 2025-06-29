import random
import threading
import eventlet
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from collections import Counter

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

zaidejai = []
sid_zemelapis = {}
zaidejo_duomenys = {}
balsai = {}
pasiruose = set()
chameleonas = None
slaptas_zodis = None
eliminuoti = set()

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
    emit('player_list', {'players': zaidejai, 'eliminated': list(eliminuoti)}, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    vardas = zaidejo_duomenys.get(sid)
    if vardas:
        zaidejai.remove(vardas)
        sid_zemelapis.pop(vardas, None)
        zaidejo_duomenys.pop(sid, None)
        pasiruose.discard(sid)
    emit('player_list', {'players': zaidejai, 'eliminated': list(eliminuoti)}, broadcast=True)

@socketio.on("start_game")
def start_game():
    global chameleonas, slaptas_zodis, eliminuoti
    eliminuoti.clear()
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
    # Only allow non-eliminated players to vote and be voted for
    aktyvus = [v for v in zaidejai if v not in eliminuoti]
    socketio.emit("voting_phase", {"players": aktyvus})

@socketio.on("submit_vote")
def submit_vote(data):
    voter_sid = request.sid
    balsaves = zaidejo_duomenys.get(voter_sid)
    if balsaves in eliminuoti:
        return  # Eliminated players can't vote
    balsas_uz = data["vote"]
    balsai[balsaves] = balsas_uz
    print(f"{balsaves} balsavo už {balsas_uz}")

    aktyvus = [v for v in zaidejai if v not in eliminuoti]
    # --- CHAMELEON AUTO-WIN LOGIC ---
    if len(aktyvus) == 2 and chameleonas in aktyvus:
        # Chameleon wins instantly
        for v in aktyvus:
            sid = sid_zemelapis.get(v)
            if sid:
                if v == chameleonas:
                    socketio.emit("chameleon_win", {}, to=sid)
                else:
                    socketio.emit("chameleon_win_others", {"chameleon": chameleonas}, to=sid)
        reset_game()
        return
    # --- END CHAMELEON AUTO-WIN LOGIC ---
    if len(balsai) == len(aktyvus):
        from collections import Counter
        balsu_sk = Counter(balsai.values())
        max_balsu = max(balsu_sk.values())
        daugiausiai = [vardas for vardas, kiek in balsu_sk.items() if kiek == max_balsu]
        if len(daugiausiai) > 1:
            print("Balsavimas lygus! Pradedamas naujas balsavimo raundas.")
            balsai.clear()
            pasiruose.clear()
            socketio.emit("tie_vote")
        else:
            eliminuotas = daugiausiai[0]
            eliminuoti.add(eliminuotas)
            sid = sid_zemelapis.get(eliminuotas)
            if sid:
                socketio.emit("eliminated", {}, to=sid)
            aktyvus_po = [v for v in zaidejai if v not in eliminuoti]
            # --- CHAMELEON AUTO-WIN LOGIC (after elimination) ---
            if len(aktyvus_po) == 2 and chameleonas in aktyvus_po:
                for v in aktyvus_po:
                    sid = sid_zemelapis.get(v)
                    if sid:
                        if v == chameleonas:
                            socketio.emit("chameleon_win", {}, to=sid)
                        else:
                            socketio.emit("chameleon_win_others", {"chameleon": chameleonas}, to=sid)
                reset_game()
                return
            # --- END CHAMELEON AUTO-WIN LOGIC ---
            if chameleonas in eliminuoti:
                for v in aktyvus_po:
                    sid = sid_zemelapis.get(v)
                    if sid:
                        socketio.emit("chameleon_lost", {"chameleon": chameleonas}, to=sid)
                reset_game()
                return
            elif len(aktyvus_po) == 1 and aktyvus_po[0] == chameleonas:
                sid = sid_zemelapis.get(chameleonas)
                if sid:
                    socketio.emit("chameleon_win", {}, to=sid)
                reset_game()
                return
            # If a non-chameleon was eliminated, start 60s discussion timer before next voting
            if eliminuotas != chameleonas:
                def start_next_voting():
                    socketio.emit("discussion_timer", {"seconds": 60})
                    def after_timer():
                        socketio.emit("next_voting_round", {"players": aktyvus_po})
                    eventlet.spawn_after(60, after_timer)
                start_next_voting()
                balsai.clear()
                pasiruose.clear()
                return
            # Otherwise, continue with next voting round
            balsai.clear()
            pasiruose.clear()
            socketio.emit("next_voting_round", {"players": aktyvus_po})

def reset_game():
    global balsai, chameleonas, slaptas_zodis, pasiruose
    balsai.clear()
    chameleonas = None
    slaptas_zodis = None
    pasiruose.clear()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
