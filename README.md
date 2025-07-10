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
  pip install flask flask-socketio eventlet --break-system-packages
```
2. Start the server:
```
   python server.py
```
## Or if you want it to auto start:
```
  sudo nano /etc/systemd/system/chameleon.service
```
1. Paste this in the editor:
```
[Unit]
Description=Chameleon Game Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/Game-chameleon-for-raspberry-pi/server.py
WorkingDirectory=/home/pi/Game-chameleon-for-raspberry-pi
Restart=always
User=pi
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
make sure you're user is pi

2. Reload systemd and enable the service
 ```
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable chameleon.service
sudo systemctl start chameleon.service
 ```
3. Check that it's running
 ```
sudo systemctl status chameleon.service
 ```
You should see “Active: active (running)”.

## to use
 Connect devices to the same Wi-Fi/hotspot and open `http://<raspberry-pi-ip>:5000` in a browser.

## Note
More languages coming soon!!!
