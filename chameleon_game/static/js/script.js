document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const nameInput = document.getElementById('nameInput');
    const joinButton = document.getElementById('joinButton');
    const gameIdInput = document.getElementById('gameIdInput'); // Get the game ID input
    const lobby = document.getElementById('lobby');
    const gameScreen = document.getElementById('gameScreen');
    const clueInput = document.getElementById('clueInput');
    const clueButton = document.getElementById('clueButton');
    const voteButton = document.getElementById('voteButton');
    const resultsScreen = document.getElementById('resultsScreen');
    const playerList = document.getElementById('playerList'); // Get the player list element
    const startGameButton = document.getElementById('startGameButton');

    let playerName;
    let gameId;
    let isChameleon = false;

    joinButton.addEventListener('click', () => {
        playerName = nameInput.value;
        gameId = gameIdInput.value; // Get the game ID from the input
        if (playerName && gameId) {
            socket.emit('join', { username: playerName, game_id: gameId }); // Send game ID
            lobby.style.display = 'none';
            gameScreen.style.display = 'block';
        }
    });

    socket.on('player_joined', (data) => {
        console.log('Player joined:', data);
        updatePlayerList(data.players);
    });

    socket.on('game_started', (data) => {
        isChameleon = data.chameleon === playerName;
        document.getElementById('word').innerText = data.word;
        document.getElementById('role').innerText = isChameleon ? 'Chameleon' : 'Not Chameleon';
    });

    clueButton.addEventListener('click', () => {
        const clue = clueInput.value;
        socket.emit('submit_clue', { clue: clue, playerName: playerName });
        clueInput.value = '';
    });

    socket.on('update_clues', (clues) => {
        // Update UI with received clues
    });

    voteButton.addEventListener('click', () => {
        const votedPlayer = document.querySelector('input[name="vote"]:checked').value;
        socket.emit('vote', votedPlayer);
    });

    socket.on('show_results', (results) => {
        // Update UI with results
        resultsScreen.style.display = 'block';
    });

    function updatePlayerList(players) {
        playerList.innerHTML = ''; // Clear existing list
        players.forEach(player => {
            const li = document.createElement('li');
            li.textContent = player;
            playerList.appendChild(li);
        });
    }

    if (startGameButton) {
        startGameButton.addEventListener('click', () => {
            socket.emit('start_game');
        });
    }

    socket.on('enable_start_button', () => {
        console.log("Received enable_start_button");
        if (startGameButton) {
            startGameButton.disabled = false;
        }
    });

    socket.on('not_enough_players', () => {
        alert("Not enough players to start the game!");
    });
    
    socket.on('not_host', () => {
        alert("You are not the host of this game!");
    });
});