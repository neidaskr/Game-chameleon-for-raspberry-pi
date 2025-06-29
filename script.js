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
    document.body.innerHTML = "";

    const card = document.createElement("div");
    card.className = "card";
    card.id = "gameScreen";

    const roleHeader = document.createElement("h2");
    const message = document.createElement("p");

    if (data.role === "chameleon") {
      roleHeader.innerHTML = `🦎 You are the <span style="color:red">Chameleon</span>!`;
      message.innerText = "Pretend you know the secret word.";
    } else {
      roleHeader.innerHTML = `✅ You are not the Chameleon.`;
      message.innerHTML = `The secret word is: <strong style="color:lime">${data.word}</strong>`;
    }

    const timer = document.createElement("h3");
    timer.id = "timer";
    timer.innerText = "Waiting for others...";

    card.appendChild(roleHeader);
    card.appendChild(message);
    card.appendChild(timer);

    document.body.appendChild(card);

    socket.emit("client_ready");
  });

  socket.on("start_timer", () => {
    const timer = document.getElementById("timer");
    timer.innerText = "Game starts in 10 seconds...";

    setTimeout(() => {
      let timeLeft = 60;
      timer.innerText = `🕒 Time left: ${timeLeft}s`;

      const countdown = setInterval(() => {
        timeLeft--;
        if (timeLeft > 0) {
          timer.innerText = `🕒 Time left: ${timeLeft}s`;
        } else {
          clearInterval(countdown);
          timer.innerText = "Time is up!";
          socket.emit("request_player_list");
        }
      }, 1000);
    }, 10000);
  });

  socket.on("voting_phase", (data) => {
    document.body.innerHTML = "";
    const card = document.createElement("div");
    card.className = "card";
    card.id = "voteContainer";

    const title = document.createElement("h3");
    title.innerText = "Who do you think is the Chameleon?";
    card.appendChild(title);

    data.players.forEach((player) => {
      const btn = document.createElement("button");
      btn.innerText = player;
      btn.onclick = () => {
        socket.emit("submit_vote", { vote: player });
        card.innerHTML = `<p>You voted for <strong>${player}</strong>. Waiting for others...</p>`;
      };
      card.appendChild(btn);
    });

    document.body.appendChild(card);
  });

  socket.on("voting_result", (data) => {
    document.body.innerHTML = "";

    const card = document.createElement("div");
    card.className = "card";
    card.id = "results";

    const title = document.createElement("h3");
    title.innerText = "🗳️ Voting Results";
    card.appendChild(title);

    for (const [voter, voted] of Object.entries(data.votes)) {
      const line = document.createElement("p");
      line.innerText = `${voter} voted for ${voted}`;
      card.appendChild(line);
    }

    const reveal = document.createElement("h3");
    reveal.style.marginTop = "1.5rem";
    reveal.innerHTML = `🦎 The Chameleon was: <span style="color:red">${data.chameleon}</span>`;
    card.appendChild(reveal);

    const restartBtn = document.createElement("button");
    restartBtn.className = "red";
    restartBtn.innerText = "🔄 Play Again";
    restartBtn.onclick = () => window.location.reload();
    card.appendChild(restartBtn);

    document.body.appendChild(card);
  });
};
