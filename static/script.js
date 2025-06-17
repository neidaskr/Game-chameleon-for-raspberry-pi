const socket = io();
let mySid = null;
let isHost = false;

const joinSection = document.getElementById('join-section');
const lobbySection = document.getElementById('lobby-section');
const nameInput = document.getElementById('name-input');
const joinBtn = document.getElementById('join-btn');
const playersList = document.getElementById('players-list');
const startBtn = document.getElementById('start-btn');

joinBtn.onclick = () => {
    const name = nameInput.value.trim();
    if (name.length > 0) {
        socket.emit('join', { name });
        joinSection.style.display = 'none';
        lobbySection.style.display = '';
    }
};

socket.on('connect', () => {
    mySid = socket.id;
});

socket.on('lobby_update', data => {
    playersList.innerHTML = '';
    data.players.forEach((player, idx) => {
        const li = document.createElement('li');
        li.textContent = player + (idx === 0 ? " (Host)" : "");
        playersList.appendChild(li);
    });
    isHost = (mySid === data.host_sid);
    startBtn.style.display = isHost ? '' : 'none';
});

startBtn.onclick = () => {
    socket.emit('start_game');
};

socket.on('game_started', () => {
    startBtn.disabled = true;
    startBtn.textContent = "Game Starting...";
});
