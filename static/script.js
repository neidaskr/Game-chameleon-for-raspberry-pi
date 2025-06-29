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

    // Remove lobby card
    const lobbyCard = document.querySelector('.lobby-card');
    if (lobbyCard) lobbyCard.remove();

    // Create a simple role card
    const roleCard = document.createElement("div");
    roleCard.className = "role-card";
    roleCard.style.background = "#fff";
    roleCard.style.borderRadius = "0.5rem";
    roleCard.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    roleCard.style.padding = "1.2rem 1rem";
    roleCard.style.maxWidth = "300px";
    roleCard.style.width = "100%";
    roleCard.style.textAlign = "center";
    roleCard.style.margin = "40px auto";
    roleCard.style.border = "1px solid #e0e0e0";

    if (data.role === "chameleon") {
      roleCard.innerHTML = `
        <div style="font-size:2.2rem;">🦎</div>
        <h2 style="color:#1a237e; font-size:1.1rem; font-weight:700;">You are the Chameleon!</h2>
        <p style="font-size:1rem; color:#3949ab;">Try to blend in and guess the word!</p>
      `;
    } else {
      roleCard.innerHTML = `
        <div style="font-size:2.2rem;">🦎</div>
        <h2 style="color:#1a237e; font-size:1.1rem; font-weight:700;">You are NOT the Chameleon!</h2>
        <p style="font-size:1rem; color:#3949ab;">The secret word is:</p>
        <div style="font-size:1.3rem; font-weight:700; color:#1a237e; margin:1rem 0;">${data.word}</div>
        <p style="font-size:0.95rem; color:#888;">Keep it secret from the Chameleon!</p>
      `;
    }

    // Add timer placeholder
    const timer = document.createElement("h3");
    timer.id = "timer";
    timer.innerText = "Waiting for others...";
    timer.style.color = "#3949ab";
    roleCard.appendChild(timer);
    document.body.appendChild(roleCard);

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
