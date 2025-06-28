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
  gameScreen.style.textAlign = "center";
  gameScreen.style.marginTop = "50px";

  if (data.role === "chameleon") {
    gameScreen.innerHTML = `
      <h2>You are the <span style="color:red">Chameleon</span>!</h2>
      <p>Pretend you know the word!</p>
    `;
  } else {
    gameScreen.innerHTML = `
      <h2>The word is: <span style="color:green">${data.word}</span></h2>
    `;
  }

  const timer = document.createElement("h3");
  timer.id = "timer";
  timer.innerText = "Waiting for everyone to get ready...";
  gameScreen.appendChild(timer);
  document.body.appendChild(gameScreen);

  // Notify server that this client is ready
  socket.emit("client_ready");
});


socket.on("join_error", data => {
  alert(data.message);
});
socket.on("player_list", data => {
  const voteContainer = document.createElement("div");
  voteContainer.id = "voteContainer";
  voteContainer.innerHTML = "<h3>Who do you think is the Chameleon?</h3>";

  data.players.forEach(player => {
    const btn = document.createElement("button");
    btn.innerText = player;
    btn.onclick = () => {
      socket.emit("submit_vote", { vote: player });
      voteContainer.innerHTML = `<p>You voted for <b>${player}</b>. Waiting for others...</p>`;
    };
    voteContainer.appendChild(btn);
    voteContainer.appendChild(document.createElement("br"));
  });

  document.body.appendChild(voteContainer);
});
socket.on("voting_result", data => {
  const resultDiv = document.createElement("div");
  resultDiv.innerHTML = "<h3>Voting Results:</h3>";

  for (const [voter, voted] of Object.entries(data.votes)) {
    const line = document.createElement("p");
    line.innerText = `${voter} voted for ${voted}`;
    resultDiv.appendChild(line);
  }

  document.body.appendChild(resultDiv);
});
socket.on("start_timer", () => {
  const timer = document.getElementById("timer");
  timer.innerText = "Game starts in 10 seconds...";

  setTimeout(() => {
    let timeLeft = 60;
    timer.innerText = `Time left: ${timeLeft}s`;

    const countdown = setInterval(() => {
      timeLeft--;
      if (timeLeft > 0) {
        timer.innerText = `Time left: ${timeLeft}s`;
      } else {
        clearInterval(countdown);
        timer.innerText = "Time is up!";
        socket.emit("request_player_list"); // Start voting
      }
    }, 1000);
  }, 10000); // Delay before actual timer
});
