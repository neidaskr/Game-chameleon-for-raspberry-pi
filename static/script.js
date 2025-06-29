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
      alert("Įveskite savo vardą");
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
        <h2 style="color:#1a237e; font-size:1.1rem; font-weight:700;">Jūs esate Chameleonas!</h2>
        <p style="font-size:1rem; color:#3949ab;">Bandykite atspėti žodį!</p>
      `;
    } else {
      roleCard.innerHTML = `
        <div style="font-size:2.2rem;">🦎</div>
        <h2 style="color:#1a237e; font-size:1.1rem; font-weight:700;">Jūs nesate Chameleonas!</h2>
        <p style="font-size:1rem; color:#3949ab;">Slaptas žodis:</p>
        <div style="font-size:1.3rem; font-weight:700; color:#1a237e; margin:1rem 0;">${data.word}</div>
        <p style="font-size:0.95rem; color:#888;">Neleiskite Chameleonui sužinoti žodžio!</p>
      `;
    }

    // Add timer placeholder
    const timer = document.createElement("h3");
    timer.id = "timer";
    timer.innerText = "Laukiama kitų žaidėjų...";
    timer.style.color = "#3949ab";
    roleCard.appendChild(timer);
    document.body.appendChild(roleCard);

    socket.emit("client_ready");
  });

  socket.on("start_timer", () => {
    if (!hasJoined) return;

    const timer = document.getElementById("timer");
    timer.innerText = "Žaidimas prasidės po 10 sekundžių...";

    setTimeout(() => {
      let timeLeft = 60;
      timer.innerText = `Likęs laikas: ${timeLeft}s`;

      const countdown = setInterval(() => {
        timeLeft--;
        if (timeLeft > 0) {
          timer.innerText = `Likęs laikas: ${timeLeft}s`;
        } else {
          clearInterval(countdown);
          timer.innerText = "Laikas baigėsi!";
          socket.emit("request_player_list");
        }
      }, 1000);
    }, 10000);
  });

  // ✅ Only this triggers the voting phase
  socket.on("voting_phase", (data) => {
    if (!hasJoined) return;

    // Remove any previous voting/result screens
    const oldVote = document.getElementById("voteContainer");
    if (oldVote) oldVote.remove();
    const oldRole = document.querySelector('.role-card');
    if (oldRole) oldRole.remove();

    // Create voting card
    const voteContainer = document.createElement("div");
    voteContainer.id = "voteContainer";
    voteContainer.style.background = "#fff";
    voteContainer.style.borderRadius = "0.5rem";
    voteContainer.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    voteContainer.style.padding = "1.2rem 1rem";
    voteContainer.style.maxWidth = "300px";
    voteContainer.style.width = "100%";
    voteContainer.style.textAlign = "center";
    voteContainer.style.margin = "40px auto";
    voteContainer.style.border = "1px solid #e0e0e0";

    voteContainer.innerHTML = "<h3 style='color:#1a237e; font-size:1.1rem; margin-bottom:1rem;'>Kas, jūsų manymu, yra Chameleonas?</h3>";

    data.players.forEach((player) => {
      const btn = document.createElement("button");
      btn.innerText = player;
      btn.style.margin = "5px";
      btn.style.padding = "0.5rem 1.2rem";
      btn.style.border = "none";
      btn.style.borderRadius = "0.7rem";
      btn.style.background = "#3949ab";
      btn.style.color = "#fff";
      btn.style.fontSize = "1rem";
      btn.style.fontWeight = "600";
      btn.style.cursor = "pointer";
      btn.style.transition = "background 0.2s";
      btn.onmouseover = () => btn.style.background = "#1a237e";
      btn.onmouseout = () => btn.style.background = "#3949ab";
      btn.onclick = () => {
        socket.emit("submit_vote", { vote: player });
        voteContainer.innerHTML = `<p>Jūs balsavote už <b>${player}</b>. Laukiama kitų...</p>`;
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
    resultDiv.innerHTML = "<h3>Balsavimo rezultatai:</h3>";

    for (const [voter, voted] of Object.entries(data.votes)) {
      const line = document.createElement("p");
      line.innerText = `${voter} balsavo už ${voted}`;
      resultDiv.appendChild(line);
    }

    resultDiv.innerHTML += `<p style="margin-top: 20px;"><strong>Chameleonas buvo: ${data.chameleon}</strong></p>`;

    const restartBtn = document.createElement("button");
    restartBtn.innerText = "Pradėti iš naujo";
    restartBtn.onclick = () => window.location.reload();
    resultDiv.appendChild(restartBtn);

    document.body.appendChild(resultDiv);
  });

  socket.on("tie_vote", () => {
    // Remove previous voting/result screens
    const oldVote = document.getElementById("voteContainer");
    if (oldVote) oldVote.remove();
    const oldResult = document.querySelector(".role-card");
    if (oldResult) oldResult.remove();

    // Show tie message and restart timer
    const tieDiv = document.createElement("div");
    tieDiv.id = "tieDiv";
    tieDiv.style.background = "#fff";
    tieDiv.style.borderRadius = "0.5rem";
    tieDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    tieDiv.style.padding = "1.2rem 1rem";
    tieDiv.style.maxWidth = "300px";
    tieDiv.style.width = "100%";
    tieDiv.style.textAlign = "center";
    tieDiv.style.margin = "40px auto";
    tieDiv.style.border = "1px solid #e0e0e0";
    tieDiv.innerHTML = `<h3 style='color:#1a237e; font-size:1.1rem; margin-bottom:1rem;'>Balsavimas lygus! Pradedamas naujas raundas po 10 sekundžių...</h3><div id='timer'>10</div>`;
    document.body.appendChild(tieDiv);

    let timeLeft = 10;
    const timer = document.getElementById("timer");
    const tieCountdown = setInterval(() => {
      timeLeft--;
      timer.innerText = timeLeft;
      if (timeLeft <= 0) {
        clearInterval(tieCountdown);
        tieDiv.innerHTML = "<h3 style='color:#1a237e;'>Naujas balsavimo raundas!</h3>";
        setTimeout(() => {
          tieDiv.remove();
          // Re-request voting phase
          socket.emit("request_player_list");
        }, 1000);
      }
    }, 1000);
  });
};
