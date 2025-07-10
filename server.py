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

    # Didesnis lietuviškų žodžių sąrašas (daugiau nei 300 žodžių, galima plėsti dar labiau)
    zodziu_sarasas = [
        "Ananasas", "Raketa", "Pieštukas", "Povandeninis laivas", "Ugnikalnis", "Laikrodis", "Bananai", "Kompiuteris", "Knyga", "Stalas", "Kėdė", "Langas", "Durys", "Telefonas", "Automobilis", "Dviratis", "Lėktuvas", "Traukinys", "Laivas", "Batas", "Kepurė", "Šuo", "Katė", "Paukštis", "Žuvis", "Medis", "Gėlė", "Žolė", "Sniegas", "Lietus", "Saulė", "Mėnulis", "Žvaigždė", "Debesis", "Vėjas", "Ugnis", "Vanduo", "Ledas", "Dramblys", "Liūtas", "Tigras", "Meška", "Vilkas", "Lapė", "Kiškis", "Voverė", "Ežys", "Pelėda", "Varna", "Gandras", "Gulbė", "Antis", "Višta", "Kiaulė", "Karvė", "Arklys", "Ožka", "Avinas", "Viščiukas", "Žirgas", "Krokodilas", "Beždžionė", "Žirafa", "Zebras", "Kengūra", "Pingvinas", "Ruonis", "Delfinas", "Ryklys", "Vėžlys", "Koralas", "Krabas", "Aštuonkojis", "Medūza", "Bitė", "Vapsva", "Skruzdėlė", "Vabalas", "Drugelis", "Moliūgas", "Obuolys", "Kriaušė", "Slyva", "Vyšnia", "Braškė", "Avietė", "Mėlynė", "Serbentas", "Vynuogė", "Arbūzas", "Melionas", "Citrina", "Apelsinas", "Mandarinas", "Greipfrutas", "Kivis", "Persikas", "Abrikosas", "Granatas", "Figas", "Datulė", "Kokosas", "Riešutas", "Migdolas", "Lazdynas", "Pistacija", "Saulėgrąža", "Morka", "Burokas", "Bulvė", "Kopūstas", "Agurkas", "Pomidoras", "Paprika", "Baklažanas", "Cukinija", "Moliūgas", "Svogūnas", "Česnakas", "Salieras", "Petražolė", "Krapas", "Špinatas", "Ropė", "Ridikas", "Žirnis", "Pupelė", "Lęšis", "Kukurūzas", "Ryžiai", "Grikiai", "Aviža", "Kviečiai", "Rugiai", "Miežiai", "Duona", "Batonas", "Bandelė", "Pyragas", "Tortas", "Sausainis", "Medus", "Sūris", "Pienas", "Jogurtas", "Grietinė", "Sviestas", "Kefyras", "Kiaušinis", "Dešra", "Kumpis", "Šoninė", "Vištiena", "Kiauliena", "Jautiena", "Aviena", "Žuvis", "Lašiša", "Starkis", "Karšis", "Ešerys", "Lynas", "Lydeka", "Ungurys", "Menke", "Silkė", "Šamas", "Krevetė", "Midija", "Austrė", "Kalmarai", "Aštuonkojis", "Kava", "Arbata", "Sultys", "Vanduo", "Limonadas", "Kokteilis", "Alus", "Vynas", "Šampanas", "Degtinė", "Brendis", "Konjakas", "Viski", "Romos", "Likerys", "Šokoladas", "Ledai", "Cukrus", "Druska", "Pipirai", "Cinamonas", "Vanilė", "Imbieras", "Garstyčios", "Majonezas", "Kečupas", "Aliejus", "Actas", "Soja", "Makaronai", "Spagečiai", "Lazanja", "Pizza", "Hamburgeris", "Sumuštinis", "Kepta duona", "Bulvių košė", "Keptuvė", "Puodas", "Arbatinukas", "Lėkštė", "Puodelis", "Stiklinė", "Šakutė", "Peilis", "Šaukštas", "Šaukštelis", "Servetėlė", "Staltiesė", "Kėdė", "Stalas", "Sofa", "Lova", "Spinta", "Komoda", "Lentyna", "Veidrodis", "Kilimėlis", "Užuolaida", "Lempa", "Šviestuvas", "Televizorius", "Radijas", "Kompiuteris", "Planšetė", "Telefonas", "Laikrodis", "Žadintuvas", "Fotoaparatas", "Kamera", "Projektorius", "Kolonėlė", "Ausinės", "Mikrofonas", "Pultelis", "Baterija", "Pakrovėjas", "Laidas", "Jungiklis", "Lizdas", "Lemputė", "Ventiliatorius", "Šildytuvas", "Kondicionierius", "Šaldytuvas", "Šaldiklis", "Orkaitė", "Mikrobangė", "Virdulys", "Skrudintuvas", "Plaktuvas", "Virtuvė", "Vonios kambarys", "Tualetas", "Dušas", "Vonia", "Kriaušė", "Veidrodis", "Rankšluostis", "Muilas", "Šampūnas", "Dantų pasta", "Dantų šepetėlis", "Skustuvas", "Plaukų džiovintuvas", "Šukos", "Kremas", "Losjonas", "Dezodorantas", "Kvepalai", "Lūpdažis", "Tušas", "Pudra", "Šešėliai", "Nagų lakas", "Nagų žirklutės", "Dildė", "Pincetas", "Žirklės", "Adatėlė", "Siūlas", "Sagos", "Smeigtukas", "Smeigtukai", "Diržas", "Kepurė", "Šalikas", "Pirštinės", "Batai", "Šlepetės", "Kojinės", "Pėdkelnės", "Kelnės", "Šortai", "Sijonas", "Suknelė", "Marškiniai", "Palaidinė", "Megztinis", "Striukė", "Paltas", "Liemenė", "Kostiumas", "Švarkas", "Kaklaraištis", "Maudymosi kostiumėlis", "Pižama", "Chalatas", "Akiniai", "Skrybėlė", "Kuprinė", "Lagaminas", "Rankinė", "Piniginė", "Raktai", "Raktų pakabukas", "Laikrodis", "Žiedas", "Auskarai", "Vėrinys", "Apyrankė", "Segtukas", "Plaukų gumytė", "Plaukų segtukas", "Knyga", "Žurnalas", "Laikraštis", "Sąsiuvinis", "Užrašų knygelė", "Rašiklis", "Pieštukas", "Trintukas", "Liniuotė", "Skaičiuotuvas", "Popierius", "Aplankas", "Segtuvas", "Lipni juosta", "Klijai", "Žirklės", "Sąvaržėlė", "Spaustukas", "Dėžutė", "Dėklas", "Krepšys", "Dėžė", "Dėžutė", "Vokas", "Atvirukas", "Laiškas", "Paštas", "Pašto ženklas", "Siunta", "Dovana", "Žaislas", "Lėlė", "Meškiukas", "Mašinėlė", "Konstruktorius", "Lego", "Galvosūkis", "Stalo žaidimas", "Kamuolys", "Šokdynė", "Dviračio ratai", "Riedlentė", "Riedučiai", "Pačiūžos", "Snieglentė", "Slidės", "Rogutės", "Palapinė", "Miegmaišis", "Kuprinė", "Žibintuvėlis", "Kompasas", "Žemėlapis", "Peilis",  # (trumpinta dėl vietos, pridėkite daugiau žodžių pagal poreikį)
    ]
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
