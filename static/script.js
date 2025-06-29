const socket = io();
let hasJoined = false;

window.onload = () => {
  const lobbyDiv = document.getElementById("lobby");
  const nameInput = document.getElementById("nameInput");
  const joinButton = document.getElementById("joinButton");
  const startContainer = document.getElementById("startContainer");
  const startButton = document.getElementById("startButton");

  joinButton.addEventListener("click", () => {
    const name = nameInput.value.trim();
    if (!name) {
      alert("Please enter your name");
      return;
    }

    socket.emit("join", { name });
    hasJoined = true;
    joinButton.disabled = true;
    nameInput.disabled = true;
  });

  startButton.addEventListener("click", () => {
    socket.emit("start_game");
    startContainer.style.display = "none";
  });

  socket.on("join_error", (data) => {
    alert(data.message);
    joinButton.disabled = false;
    nameInput.disabled = false;
  });

  socket.on("player_list", (data) => {
    if (!hasJoined) return;
    if (data.players.length >= 2) {
      startContainer.style.display = "block";
    } else {
      startContainer.style.display = "none";
    }
  });

  socket.on("game_data", (data) => {
    if (!hasJoined) return;

    lobbyDiv.style.display = "none";

    const gameScreen = document.createElement("div");
    gameScreen.id = "gameScreen";

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
    timer.innerText = "Waiting for others...";
    gameScreen.appendChild(timer);
    document.body.appendChild(gameScreen);

    socket.emit("client_ready");
  });

  socket.on("start_timer", () => {
    if (!hasJoined) return;

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
          socket.emit("request_player_list");
        }
      }, 1000);
    }, 10000);
  });

  // ✅ Only this triggers the voting phase
  socket.on("voting_phase", (data) => {
    if (!hasJoined) return;

    const voteContainer = document.createElement("div");
    voteContainer.id = "voteContainer";
    voteContainer.innerHTML = "<h3>Who do you think is the Chameleon?</h3>";

    data.players.forEach((player) => {
      const btn = document.createElement("button");
      btn.innerText = player;
      btn.style.margin = "5px";
      btn.onclick = () => {
        socket.emit("submit_vote", { vote: player });
        voteContainer.innerHTML = `<p>You voted for <b>${player}</b>. Waiting for others...</p>`;
      };
      voteContainer.appendChild(btn);
    });

    document.body.appendChild(voteContainer);
  });

  socket.on("voting_result", (data) => {
    if (!hasJoined) return;

    const oldVote = document.getElementById("voteContainer");
    if (oldVote) oldVote.remove();

    const resultDiv = document.createElement("div");
    resultDiv.style.marginTop = "30px";
    resultDiv.innerHTML = "<h3>Voting Results:</h3>";

    for (const [voter, voted] of Object.entries(data.votes)) {
      const line = document.createElement("p");
      line.innerText = `${voter} voted for ${voted}`;
      resultDiv.appendChild(line);
    }

    resultDiv.innerHTML += `<p style="margin-top: 20px;"><strong>The Chameleon was: ${data.chameleon}</strong></p>`;

    const restartBtn = document.createElement("button");
    restartBtn.innerText = "Restart Game";
    restartBtn.onclick = () => window.location.reload();
    resultDiv.appendChild(restartBtn);

    document.body.appendChild(resultDiv);
  });
};
