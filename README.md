# Chameleon Game
NOT WORKING 🚫 

## Overview
Chameleon is a web-based multiplayer party game where players try to identify the "chameleon" among them. The chameleon does not know the secret word, while the other players give clues to help them guess without revealing the word. The game is designed to be played on mobile devices and is hosted on a Raspberry Pi using Flask and Flask-SocketIO.

## Features
- Multiplayer gameplay accessible via a web browser on the same local network.
- Real-time updates using WebSockets for joining, clue sharing, and voting.
- Simple session-based gameplay with no registration or database.
- Responsive design for mobile devices.

## Getting Started

### Requirements
- Raspberry Pi with Python 3 installed
- Flask
- Flask-SocketIO

### Installation
1. Clone the repository or download the project files to your Raspberry Pi.
2. Navigate to the project directory:
   ```
   cd chameleon_game
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Game
1. Start the Flask application:
   ```
   python app.py
   ```
2. Access the game in a web browser by navigating to `http://<Raspberry_Pi_IP>:5000`, where `<Raspberry_Pi_IP>` is the local IP address of your Raspberry Pi.

### Gameplay Rules
1. Players enter their names to join the game.
2. Once at least 3 players have joined, the host selects a category and a secret word.
3. Each player (except the chameleon) gives a clue related to the secret word.
4. After all clues are given, players vote on who they think is the chameleon.
5. If the chameleon is correctly identified, they get a chance to guess the secret word to win.

## Contributing
Feel free to contribute to the project by submitting issues or pull requests. 

## License
This project is open-source and available under the MIT License.