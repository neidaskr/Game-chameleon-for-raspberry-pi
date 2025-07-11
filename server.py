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
game_mode_vote = {}
game_mode = None

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
    global chameleonas, slaptas_zodis, eliminuoti, game_mode_vote, game_mode
    eliminuoti.clear()
    game_mode_vote.clear()
    game_mode = None
    if len(zaidejai) < 2:
        emit("join_error", {"message": "Reikia bent 2 žaidėjų"})
        return
    # Pradėti rėžimo balsavimą
    socketio.emit("game_mode_vote", {"modes": ["Chameleonas be žodžio", "Chameleonas su žodžiu"]})

@socketio.on("submit_game_mode_vote")
def submit_game_mode_vote(data):
    global game_mode_vote, game_mode
    sid = request.sid
    vardas = zaidejo_duomenys.get(sid)
    if not vardas:
        return
    balsas = data.get("mode")
    if balsas not in ["Chameleonas be žodžio", "Chameleonas su žodžiu"]:
        return
    game_mode_vote[vardas] = balsas
    if len(game_mode_vote) == len(zaidejai):
        # Suskaičiuoti balsus
        rez = Counter(game_mode_vote.values())
        pasirinktas = rez.most_common(1)[0][0]
        game_mode = pasirinktas
        socketio.emit("game_mode_selected", {"mode": game_mode})
        # Pradėti žaidimą po 5 sekundžių
        def delayed_start():
            eventlet.sleep(5)
            start_real_game()
        eventlet.spawn(delayed_start)

def start_real_game():
    global chameleonas, slaptas_zodis, game_mode
    # Pagrindinis žodžių sąrašas
    zodziu_sarasas = [
        "Ananasas", "Raketa", "Pieštukas", "Povandeninis laivas", "Ugnikalnis", "Laikrodis", "Bananai", "Kompiuteris", "Knyga", "Stalas", "Kėdė", "Langas", "Durys", "Telefonas", "Automobilis", "Dviratis", "Lėktuvas", "Traukinys", "Laivas", "Batas", "Kepurė", "Šuo", "Katė", "Paukštis", "Žuvis", "Medis", "Gėlė", "Žolė", "Sniegas", "Lietus", "Saulė", "Mėnulis", "Žvaigždė", "Debesis", "Vėjas", "Ugnis", "Vanduo", "Ledas", "Dramblys", "Liūtas", "Tigras", "Meška", "Vilkas", "Lapė", "Kiškis", "Voverė", "Ežys", "Pelėda", "Varna", "Gandras", "Gulbė", "Antis", "Višta", "Kiaulė", "Karvė", "Arklys", "Ožka", "Avinas", "Viščiukas", "Žirgas", "Krokodilas", "Beždžionė", "Žirafa", "Zebras", "Kengūra", "Pingvinas", "Ruonis", "Delfinas", "Ryklys", "Vėžlys", "Koralas", "Krabas", "Aštuonkojis", "Medūza", "Bitė", "Vapsva", "Skruzdėlė", "Vabalas", "Drugelis", "Moliūgas", "Obuolys", "Kriaušė", "Slyva", "Vyšnia", "Braškė", "Avietė", "Mėlynė", "Serbentas", "Vynuogė", "Arbūzas", "Melionas", "Citrina", "Apelsinas", "Mandarinas", "Greipfrutas", "Kivis", "Persikas", "Abrikosas", "Granatas", "Figas", "Datulė", "Kokosas", "Riešutas", "Migdolas", "Lazdynas", "Pistacija", "Saulėgrąža", "Morka", "Burokas", "Bulvė", "Kopūstas", "Agurkas", "Pomidoras", "Paprika", "Baklažanas", "Cukinija", "Moliūgas", "Svogūnas", "Česnakas", "Salieras", "Petražolė", "Krapas", "Špinatas", "Ropė", "Ridikas", "Žirnis", "Pupelė", "Lęšis", "Kukurūzas", "Ryžiai", "Grikiai", "Aviža", "Kviečiai", "Rugiai", "Miežiai", "Duona", "Batonas", "Bandelė", "Pyragas", "Tortas", "Sausainis", "Medus", "Sūris", "Pienas", "Jogurtas", "Grietinė", "Sviestas", "Kefyras", "Kiaušinis", "Dešra", "Kumpis", "Šoninė", "Vištiena", "Kiauliena", "Jautiena", "Aviena", "Žuvis", "Lašiša", "Starkis", "Karšis", "Ešerys", "Lynas", "Lydeka", "Ungurys", "Menke", "Silkė", "Šamas", "Krevetė", "Midija", "Austrė", "Kalmarai", "Aštuonkojis", "Kava", "Arbata", "Sultys", "Vanduo", "Limonadas", "Kokteilis", "Alus", "Vynas", "Šampanas", "Degtinė", "Brendis", "Konjakas", "Viski", "Romos", "Likerys", "Šokoladas", "Ledai", "Cukrus", "Druska", "Pipirai", "Cinamonas", "Vanilė", "Imbieras", "Garstyčios", "Majonezas", "Kečupas", "Aliejus", "Actas", "Soja", "Makaronai", "Spagečiai", "Lazanja", "Pizza", "Hamburgeris", "Sumuštinis", "Kepta duona", "Bulvių košė", "Keptuvė", "Puodas", "Arbatinukas", "Lėkštė", "Puodelis", "Stiklinė", "Šakutė", "Peilis", "Šaukštas", "Šaukštelis", "Servetėlė", "Staltiesė", "Kėdė", "Stalas", "Sofa", "Lova", "Spinta", "Komoda", "Lentyna", "Veidrodis", "Kilimėlis", "Užuolaida", "Lempa", "Šviestuvas", "Televizorius", "Radijas", "Kompiuteris", "Planšetė", "Telefonas", "Laikrodis", "Žadintuvas", "Fotoaparatas", "Kamera", "Projektorius", "Kolonėlė", "Ausinės", "Mikrofonas", "Pultelis", "Baterija", "Pakrovėjas", "Laidas", "Jungiklis", "Lizdas", "Lemputė", "Ventiliatorius", "Šildytuvas", "Kondicionierius", "Šaldytuvas", "Šaldiklis", "Orkaitė", "Mikrobangė", "Virdulys", "Skrudintuvas", "Plaktuvas", "Virtuvė", "Vonios kambarys", "Tualetas", "Dušas", "Vonia", "Kriaušė", "Veidrodis", "Rankšluostis", "Muilas", "Šampūnas", "Dantų pasta", "Dantų šepetėlis", "Skustuvas", "Plaukų džiovintuvas", "Šukos", "Kremas", "Losjonas", "Dezodorantas", "Kvepalai", "Lūpdažis", "Tušas", "Pudra", "Šešėliai", "Nagų lakas", "Nagų žirklutės", "Dildė", "Pincetas", "Žirklės", "Adatėlė", "Siūlas", "Sagos", "Smeigtukas", "Smeigtukai", "Diržas", "Kepurė", "Šalikas", "Pirštinės", "Batai", "Šlepetės", "Kojinės", "Pėdkelnės", "Kelnės", "Šortai", "Sijonas", "Suknelė", "Marškiniai", "Palaidinė", "Megztinis", "Striukė", "Paltas", "Liemenė", "Kostiumas", "Švarkas", "Kaklaraištis", "Maudymosi kostiumėlis", "Pižama", "Chalatas", "Akiniai", "Skrybėlė", "Kuprinė", "Lagaminas", "Rankinė", "Piniginė", "Raktai", "Raktų pakabukas", "Laikrodis", "Žiedas", "Auskarai", "Vėrinys", "Apyrankė", "Segtukas", "Plaukų gumytė", "Plaukų segtukas", "Knyga", "Žurnalas", "Laikraštis", "Sąsiuvinis", "Užrašų knygelė", "Rašiklis", "Pieštukas", "Trintukas", "Liniuotė", "Skaičiuotuvas", "Popierius", "Aplankas", "Segtuvas", "Lipni juosta", "Klijai", "Žirklės", "Sąvaržėlė", "Spaustukas", "Dėžutė", "Dėklas", "Krepšys", "Dėžė", "Dėžutė", "Vokas", "Atvirukas", "Laiškas", "Paštas", "Pašto ženklas", "Siunta", "Dovana", "Žaislas", "Lėlė", "Meškiukas", "Mašinėlė", "Konstruktorius", "Lego", "Galvosūkis", "Stalo žaidimas", "Kamuolys", "Šokdynė", "Dviračio ratai", "Riedlentė", "Riedučiai", "Pačiūžos", "Snieglentė", "Slidės", "Rogutės", "Palapinė", "Miegmaišis", "Kuprinė", "Žibintuvėlis", "Kompasas", "Žemėlapis", "Peilis"
    ]
    # Alternatyvus žodžių sąrašas chameleonui (turi būti tokio pat ilgio kaip pagrindinis)
    chameleon_zodziai = [

        "Mango", "Palydovas", "Rašiklis", "Laivas", "Vulkanas", "Kalendorius", "Kokosas", "Planšetė", "Žurnalas", "Suolas", "Taburetė", "Stiklas", "Vartai", "Išmanusis", "Motociklas", "Paspirtukas", "Autobusas", "Sraigtasparnis", "Metro", "Jachta", "Šlepetė", "Šalmas", "Katinas", "Triušis", "Gaidys", "Vėžys", "Krūmas", "Tulipanas", "Samanos", "Ledinukas", "Rūkas", "Žibintas", "Saturnas", "Kometa", "Rūkas", "Liepsna", "Upė", "Sniegas", "Mamutai", "Tigras", "Leopardas", "Barsukas", "Šernas", "Šakalys", "Žebenkštis", "Žiurkėnas", "Žaltys", "Garnys", "Balandis", "Žąsis", "Kregždė", "Karvelis", "Putpelė", "Žąsis", "Ožys", "Briedis", "Elnias", "Stumbras", "Višta", "Asilas", "Mulė", "Kupranugaris", "Mandrilas", "Orangutanas", "Okapė", "Antilopė", "Lama", "Alpaka", "Jūrų liūtas", "Jūrų arkliukas", "Marlinas", "Kardžuvė", "Koralas", "Krabas", "Sepija", "Jūrų žvaigždė", "Širšė", "Bitė", "Termitas", "Skorpionas", "Laumžirgis", "Avietė", "Gervuogė", "Spanguolė", "Šermukšnis", "Obuolys", "Kriaušė", "Slyva", "Vyšnia", "Braškė", "Mėlynė", "Serbentas", "Vynuogė", "Arbūzas", "Melionas", "Citrina", "Apelsinas", "Mandarinas", "Greipfrutas", "Kivis", "Persikas", "Abrikosas", "Granatas", "Figas", "Datulė", "Kokosas", "Riešutas", "Migdolas", "Lazdynas", "Pistacija", "Saulėgrąža", "Pastarnokas", "Ridikas", "Topinambas", "Salota", "Moliūgas", "Baklažanas", "Cukinija", "Paprika", "Pomidoras", "Svogūnas", "Poras", "Česnakas", "Krapai", "Petražolė", "Salieras", "Špinatai", "Ropė", "Ridikėlis", "Žirnis", "Pupelė", "Lęšis", "Kukurūzas", "Sorgas", "Grikiai", "Aviža", "Kviečiai", "Rugiai", "Miežiai", "Bagetė", "Riestainis", "Keksiukas", "Biskvitas", "Pyragaitis", "Tortas", "Pyragėlis", "Meduolis", "Sirupas", "Varškė", "Grietinėlė", "Sviestas", "Kefyras", "Kiaušinienė", "Salami", "Šoninė", "Vištiena", "Kiauliena", "Jautiena", "Aviena", "Menke", "Lašiša", "Starkis", "Karšis", "Ešerys", "Lynas", "Lydeka", "Ungurys", "Silkė", "Šamas", "Krevetė", "Midija", "Austrė", "Kalmarai", "Sepija", "Espresso", "Žalioji arbata", "Obuolių sultys", "Mineralinis", "Gazuotas vanduo", "Margarita", "Sidras", "Portveinas", "Prosecco", "Tekila", "Grappa", "Armanjakas", "Burbonas", "Romas", "Vermutai", "Karamelė", "Jogurtiniai ledai", "Glajus", "Druska", "Pipirai", "Ciberžolė", "Muskatas", "Kardamonas", "Kmynai", "Majonezas", "Kečupas", "Aliejus", "Actas", "Sojos padažas", "Tagliatelle", "Fusilli", "Lazanja", "Focaccia", "Hotdogas", "Tostas", "Krekeris", "Bulvių plokštainis", "Keptuvė", "Puodas", "Arbatinukas", "Lėkštė", "Puodelis", "Stiklinė", "Šakutė", "Peilis", "Šaukštas", "Šaukštelis", "Servetėlė", "Staltiesė", "Taburetė", "Rašomasis stalas", "Fotelis", "Dvivietė lova", "Spintelė", "Komoda", "Lentynėlė", "Veidrodis", "Kilimėlis", "Užuolaida", "Lemputė", "Šviestuvas", "Monitorius", "Radijo imtuvas", "Nešiojamas kompiuteris", "E-knygų skaityklė", "Išmanusis laikrodis", "Žadintuvas", "Veidrodinis fotoaparatas", "Web kamera", "Projektorius", "Kolonėlė", "Ausinės", "Mikrofonas", "Pultelis", "Baterija", "Pakrovėjas", "Laidas", "Jungiklis", "Lizdas", "Lemputė", "Ventiliatorius", "Šildytuvas", "Kondicionierius", "Šaldytuvas", "Šaldiklis", "Orkaitė", "Mikrobangė", "Virdulys", "Skrudintuvas", "Plaktuvas", "Virtuvė", "Vonios kambarys", "Tualetas", "Dušas", "Vonia", "Bidė", "Kosmetinis veidrodis", "Rankšluostis", "Muilinė", "Kondicionierius", "Dantų siūlas", "Burnos skalavimo skystis", "Barzdaskutė", "Plaukų tiesintuvas", "Šukos", "Kremas", "Losjonas", "Dezodorantas", "Kvepalai", "Lūpų balzamas", "Akių pieštukas", "Pudra", "Šešėliai", "Nagų lakas", "Nagų dildė", "Nagų žnyplutės", "Pincetas", "Žirklės", "Adatėlė", "Siūlas", "Sagos", "Smeigtukas", "Smeigtukai", "Diržas", "Kepurė", "Šalikas", "Pirštinės", "Batai", "Šlepetės", "Kojinės", "Pėdkelnės", "Kelnės", "Šortai", "Sijonas", "Suknelė", "Marškiniai", "Palaidinė", "Megztinis", "Striukė", "Paltas", "Liemenė", "Kostiumas", "Švarkas", "Kaklaraištis", "Maudymosi šortai", "Naktiniai", "Chalatas", "Akiniai nuo saulės", "Kepuraitė", "Kelioninis krepšys", "Lagaminas", "Rankinė", "Piniginė", "Raktų ryšulys", "Raktų pakabukas", "Laikrodis", "Žiedas", "Auskarai", "Vėrinys", "Apyrankė", "Segtukas", "Plaukų segtukas", "Plaukų gumytė", "Romanas", "Komiksas", "Dienraštis", "Užrašų knyga", "Užrašų lapelis", "Flomasteris", "Pieštukas", "Trintukas", "Liniuotė", "Skaičiuotuvas", "Popierius", "Aplankas", "Segtuvas", "Lipni juosta", "Klijai", "Žirklės", "Sąvaržėlė", "Spaustukas", "Dėžutė", "Dėklas", "Krepšys", "Dėžė", "Dėžutė", "Vokas", "Atvirukas", "Laiškas", "Paštas", "Pašto ženklas", "Siunta", "Dovana", "Žaislas", "Lėlė", "Meškiukas", "Mašinėlė", "Konstruktorius", "Lego", "Galvosūkis", "Stalo žaidimas", "Kamuolys", "Šokdynė", "Dviračio ratai", "Riedlentė", "Riedučiai", "Pačiūžos", "Snieglentė", "Slidės", "Rogutės", "Palapinė", "Miegmaišis", "Kuprinė", "Žibintuvėlis", "Kompasas", "Žemėlapis", "Peilis"
    ]



    for zaidejas in zaidejai:
        sid = sid_zemelapis[zaidejas]
        if zaidejas == chameleonas:
            if game_mode == "Chameleonas su žodžiu":
                # Parinkti panašų žodį (kitą iš sąrašo, kuris nėra slaptas_zodis)
                galimi = [z for z in zodziu_sarasas if z != slaptas_zodis]
                panasus = random.choice(galimi) if galimi else "?"
                socketio.emit("game_data", {"role": "chameleon", "word": panasus, "mode": game_mode}, room=sid)
            else:
                socketio.emit("game_data", {"role": "chameleon", "word": None, "mode": game_mode}, room=sid)
        else:
            socketio.emit("game_data", {"role": "player", "word": slaptas_zodis, "mode": game_mode}, room=sid)
    print(f"Žaidimas prasidėjo: {slaptas_zodis}, Chameleonas: {chameleonas}")
    # Pradėti žaidimo laikmatį visiems po rolių išdavimo
    socketio.emit("start_timer")

@socketio.on("make_guess")
def handle_guess(data):
    global eliminuoti
    sid = request.sid
    vardas = zaidejo_duomenys.get(sid)
    if not vardas or vardas == chameleonas:
        return
    spėjimas = data.get("guess")
    if spėjimas == slaptas_zodis:
        # Teisingas spėjimas, žaidėjas laimi
        emit("guess_result", {"success": True, "message": "Teisingai! Žodis buvo: " + slaptas_zodis})
        # Visi kiti žaidėjai eliminuojami
        for zaidejas in zaidejai:
            if zaidejas != chameleonas:
                sid = sid_zemelapis[zaidejas]
                emit("player_eliminated", {"player": zaidejas}, room=sid)
                eliminuoti.add(zaidejas)
        # Chameleonas laimi
        sid = sid_zemelapis[chameleonas]
        emit("game_won", {"winner": chameleonas}, room=sid)
        print(f"Žaidimą laimėjo {chameleonas} su žodžiu {slaptas_zodis}!")
    else:
        emit("guess_result", {"success": False, "message": "Neteisingas spėjimas."})

@socketio.on("get_player_data")
def handle_get_player_data():
    sid = request.sid
    vardas = zaidejo_duomenys.get(sid)
    if vardas:
        emit("player_data", {"name": vardas, "eliminated": vardas in eliminuoti, "ready": sid in pasiruose})

@socketio.on("toggle_ready")
def handle_toggle_ready():
    sid = request.sid
    if sid in pasiruose:
        pasiruose.remove(sid)
    else:
        pasiruose.add(sid)
    emit("player_list", {'players': zaidejai, 'eliminated': list(eliminuoti)}, broadcast=True)

@socketio.on("start_timer_done")
def handle_start_timer_done():
    # Kai klientas praneša, kad laikmatis baigėsi, pradėti balsavimą visiems
    # Siunčiamas voting_phase su žaidėjų sąrašu
    socketio.emit("voting_phase", {"players": zaidejai})

@socketio.on("submit_vote")
def handle_submit_vote(data):
    global balsai
    sid = request.sid
    vardas = zaidejo_duomenys.get(sid)
    if not vardas or vardas in eliminuoti:
        return
    balsas = data.get("vote")
    if balsas not in zaidejai or balsas in eliminuoti:
        return
    if not hasattr(handle_submit_vote, "votes"):
        handle_submit_vote.votes = {}
    handle_submit_vote.votes[vardas] = balsas
    # Kai visi gyvi žaidėjai prabalsavo, skaičiuojam rezultatus
    gyvi = [z for z in zaidejai if z not in eliminuoti]
    if len(handle_submit_vote.votes) == len(gyvi):
        balsai = handle_submit_vote.votes.copy()
        # Suskaičiuoti balsus
        balsuotos = list(balsai.values())
        if balsuotos:
            from collections import Counter
            rez = Counter(balsuotos)
            daugiausia = rez.most_common(1)[0][1]
            top = [k for k, v in rez.items() if v == daugiausia]
            if len(top) > 1:
                # Lygiosios
                socketio.emit("tie_vote")
            else:
                eliminuotas = top[0]
                eliminuoti.add(eliminuotas)
                socketio.emit("player_eliminated", {"player": eliminuotas})
                # Pranešti rezultatus
                socketio.emit("voting_result", {"votes": balsai, "chameleon": chameleonas, "eliminated": eliminuotas, "chameleon_found": False})
                # Patikrinti ar žaidimas baigėsi
                if eliminuotas == chameleonas:
                    socketio.emit("chameleon_lost", {"chameleon": chameleonas})
                elif len(gyvi) - 1 <= 2:
                    socketio.emit("chameleon_win_others", {"chameleon": chameleonas})
        handle_submit_vote.votes = {}

def main():
    socketio.run(app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()