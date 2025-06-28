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
socket.on("game_data", data => {
    document.getElementById("lobby").style.display = "none";
    const gameScreen = document.createElement("div");
    gameScreen.id = "gameScreen";

    if (data.role === "chameleon") {
        gameScreen.innerHTML = "<h2>You are the <span style='color:red'>Chameleon</span>! Act like you know the word!</h2>";
    } else {
        gameScreen.innerHTML = `<h2>The word is: <span style='color:green'>${data.word}</span></h2>`;
    }

    document.body.appendChild(gameScreen);
});
socket.on("join_error", data => {
  alert(data.message);
});
