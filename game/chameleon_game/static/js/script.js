document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const nameInput = document.getElementById('nameInput');
    const joinButton = document.getElementById('joinButton');
    const lobby = document.getElementById('lobby');
    const gameScreen = document.getElementById('gameScreen');
    const clueInput = document.getElementById('clueInput');
    const clueButton = document.getElementById('clueButton');
    const voteButton = document.getElementById('voteButton');
    const resultsScreen = document.getElementById('resultsScreen');

    let playerName;
    let isChameleon = false;

    joinButton.addEventListener('click', () => {
        playerName = nameInput.value;
        if (playerName) {
            socket.emit('join', playerName);
            lobby.style.display = 'none';
            gameScreen.style.display = 'block';
        }
    });

    socket.on('game_start', (data) => {
        isChameleon = data.isChameleon;
        // Update UI for game start
    });

    clueButton.addEventListener('click', () => {
        const clue = clueInput.value;
        socket.emit('send_clue', { clue, playerName });
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
});