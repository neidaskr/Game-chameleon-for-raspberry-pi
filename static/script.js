const socket = io();
let myName = "";

function joinGame() {
    const nameInput = document.getElementById("nameInput");
    myName = nameInput.value.trim();
    if (myName === "") return alert("Please enter a name");

    socket.emit("join", { name: myName });

    document.getElementById("joinScreen").style.display = "none";
    document.getElementById("lobby").style.display = "block";
}

socket.on("player_list", data => {
    const playerList = document.getElementById("playerList");
    playerList.innerHTML = "";
    data.players.forEach(player => {
        const li = document.createElement("li");
        li.textContent = player;
        playerList.appendChild(li);
    });
});

function startGame() {
    socket.emit("player_ready", { name: myName });
    document.getElementById("startButton").disabled = true;
    document.getElementById("startButton").textContent = "Waiting...";
}

socket.on("start_game", () => {
    document.getElementById("startButton").disabled = true;
    document.getElementById("startButton").textContent = "Game Starting...";
    alert("Game is starting!");
    // Future: redirect to game screen
});
