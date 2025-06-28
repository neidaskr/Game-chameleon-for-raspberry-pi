# Chameleon Game Lobby (Start Screen)

A modern, real-time lobby for a local-network party game (like "Chameleon"), built with Flask + Flask-SocketIO. Players join via browser, see a live-updating lobby, and the first player is the host.

## Features
- Players enter their name and join the lobby
- All joined players are listed live
- First player is the host and sees a "Start Game" button
- Real-time updates via Socket.IO
- No database, all in-memory
- Modern, responsive UI (Flexbox, Google Fonts)

## File Structure
```
server.py                # Flask server + Socket.IO
/templates/index.html    # Join/lobby UI
/static/script.js        # Socket.IO client logic
```

## Running on Raspberry Pi or Local Network
1. Install dependencies:
   ```
   pip install flask flask-socketio eventlet
   ```
2. Start the server:
   ```
   python server.py
   ```
3. Connect devices to the same Wi-Fi/hotspot and open `http://<raspberry-pi-ip>:5000` in a browser.

## Note
This is only the start screen/lobby. No game logic is included yet.
