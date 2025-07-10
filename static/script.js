const socket = io();
let hasJoined = false;
let eliminated = false; // Track if this player is eliminated

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

  // --- GAME MODE VOTE ---
  socket.on("game_mode_vote", (data) => {
    // Remove lobby card if present
    const lobbyCard = document.querySelector('.lobby-card');
    if (lobbyCard) lobbyCard.remove();
    // Remove any previous game mode vote UI
    const oldModeDiv = document.getElementById("gameModeDiv");
    if (oldModeDiv) oldModeDiv.remove();
    // Show game mode vote UI
    const modeDiv = document.createElement("div");
    modeDiv.id = "gameModeDiv";
    modeDiv.style.background = "#fff";
    modeDiv.style.borderRadius = "0.5rem";
    modeDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    modeDiv.style.padding = "1.2rem 1rem";
    modeDiv.style.maxWidth = "300px";
    modeDiv.style.width = "100%";
    modeDiv.style.textAlign = "center";
    modeDiv.style.margin = "40px auto";
    modeDiv.style.border = "1px solid #e0e0e0";
    modeDiv.innerHTML = `<h3 style='color:#1a237e; font-size:1.1rem; margin-bottom:1rem;'>Išsirinkite žaidimo rėžimą:</h3>`;
    data.modes.forEach((mode) => {
      const btn = document.createElement("button");
      btn.innerText = mode;
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
        // Disable all buttons after vote
        Array.from(modeDiv.querySelectorAll('button')).forEach(b => b.disabled = true);
        btn.style.background = "#1a237e";
        btn.innerText = "Balsas priimtas";
        socket.emit("submit_game_mode_vote", { mode });
      };
      modeDiv.appendChild(btn);
    });
    document.body.appendChild(modeDiv);
  });

  socket.on("game_mode_selected", (data) => {
    // Remove game mode vote UI
    const oldModeDiv = document.getElementById("gameModeDiv");
    if (oldModeDiv) oldModeDiv.remove();
    // Show info about selected mode
    const infoDiv = document.createElement("div");
    infoDiv.id = "modeInfoDiv";
    infoDiv.style.background = "#fff";
    infoDiv.style.borderRadius = "0.5rem";
    infoDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    infoDiv.style.padding = "1.2rem 1rem";
    infoDiv.style.maxWidth = "300px";
    infoDiv.style.width = "100%";
    infoDiv.style.textAlign = "center";
    infoDiv.style.margin = "40px auto";
    infoDiv.style.border = "1px solid #e0e0e0";
    infoDiv.innerHTML = `<h3 style='color:#1a237e; font-size:1.1rem;'>Pasirinktas rėžimas:</h3><p style='color:#3949ab; font-size:1.1rem; font-weight:600;'>${data.mode}</p><p>Laukiama žaidimo pradžios...</p>`;
    document.body.appendChild(infoDiv);
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

    // Pašalinti rėžimo info, jei yra
    const oldModeInfo = document.getElementById("modeInfoDiv");
    if (oldModeInfo) oldModeInfo.remove();

    if (data.role === "chameleon") {
      // Chameleonas (su žodžiu arba be žodžio)
      let wordHtml = "";
      if (data.word) {
        wordHtml = `<p style="font-size:1rem; color:#3949ab;">Jūsų žodis:</p><div style="font-size:1.3rem; font-weight:700; color:#1a237e; margin:1rem 0;">${data.word}</div><p style="font-size:0.95rem; color:#888;">Bandykite atspėti tikrąjį žodį!</p>`;
      } else {
        wordHtml = `<p style='font-size:1rem; color:#3949ab;'>Jūs nežinote žodžio!</p><p style='font-size:0.95rem; color:#888;'>Bandykite išsiaiškinti žodį pagal kitų užuominas.</p>`;
      }
      roleCard.innerHTML = `
        <div style="font-size:2.2rem;">🦎</div>
        <h2 style="color:#1a237e; font-size:1.1rem; font-weight:700;">Jūs esate Chameleonas!</h2>
        ${wordHtml}
      `;
    } else {
      // Paprastas žaidėjas
      roleCard.innerHTML = `
        <div style="font-size:2.2rem;">🧑‍🤝‍🧑</div>
        <h2 style="color:#1a237e; font-size:1.1rem; font-weight:700;">Jūs nesate Chameleonas</h2>
        <p style="font-size:1rem; color:#3949ab;">Slaptas žodis:</p>
        <div style="font-size:1.3rem; font-weight:700; color:#1a237e; margin:1rem 0;">${data.word}</div>
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
          // Pranešti serveriui, kad laikas baigėsi
          socket.emit("start_timer_done");
        }
      }, 1000);
    }, 10000);
  });

  // ✅ Only this triggers the voting phase
  socket.on("voting_phase", (data) => {
    if (!hasJoined || eliminated) return; // Prevent eliminated players from voting

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

    if (data.eliminated && data.eliminated !== data.chameleon) {
      resultDiv.innerHTML += `<p style='color:#d32f2f; margin-top: 20px;'><strong>Chameleonas vis dar tarp jūsų! Išbalsuotas žaidėjas: ${data.eliminated}</strong></p>`;
    } else {
      resultDiv.innerHTML += `<p style="margin-top: 20px;"><strong>Chameleonas buvo: ${data.chameleon}</strong></p>`;
    }

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

  socket.on("eliminated", () => {
    eliminated = true; // Set eliminated flag
    // Remove all game UI
    document.body.innerHTML = "";
    // Show eliminated message
    const elimDiv = document.createElement("div");
    elimDiv.style.background = "#fff";
    elimDiv.style.borderRadius = "0.5rem";
    elimDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    elimDiv.style.padding = "1.2rem 1rem";
    elimDiv.style.maxWidth = "300px";
    elimDiv.style.width = "100%";
    elimDiv.style.textAlign = "center";
    elimDiv.style.margin = "40px auto";
    elimDiv.style.border = "1px solid #e0e0e0";
    elimDiv.innerHTML = `<h2 style='color:#1a237e; font-size:1.2rem;'>Tu esi išbalsuotas.</h2><p style='color:#3949ab;'>Stebėk žaidimą kaip žiūrovas.</p>`;
    document.body.appendChild(elimDiv);
  });

  socket.on("chameleon_win", () => {
    document.body.innerHTML = "";
    const winDiv = document.createElement("div");
    winDiv.style.background = "#fff";
    winDiv.style.borderRadius = "0.5rem";
    winDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    winDiv.style.padding = "1.2rem 1rem";
    winDiv.style.maxWidth = "300px";
    winDiv.style.width = "100%";
    winDiv.style.textAlign = "center";
    winDiv.style.margin = "40px auto";
    winDiv.style.border = "1px solid #e0e0e0";
    winDiv.innerHTML = `<h2 style='color:#1a237e; font-size:1.2rem;'>Tu laimėjai!</h2><p style='color:#3949ab;'>Chameleonas išliko nepastebėtas.</p>`;
    document.body.appendChild(winDiv);
  });

  socket.on("chameleon_win_others", (data) => {
    document.body.innerHTML = "";
    const loseDiv = document.createElement("div");
    loseDiv.style.background = "#fff";
    loseDiv.style.borderRadius = "0.5rem";
    loseDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    loseDiv.style.padding = "1.2rem 1rem";
    loseDiv.style.maxWidth = "300px";
    loseDiv.style.width = "100%";
    loseDiv.style.textAlign = "center";
    loseDiv.style.margin = "40px auto";
    loseDiv.style.border = "1px solid #e0e0e0";
    loseDiv.innerHTML = `<h2 style='color:#1a237e; font-size:1.2rem;'>Chameleonas laimėjo!</h2><p style='color:#3949ab;'>Chameleonas buvo: <b>${data.chameleon}</b></p>`;
    document.body.appendChild(loseDiv);
  });

  socket.on("next_voting_round", (data) => {
    if (eliminated) return; // Prevent eliminated players from voting
    // Remove any previous voting/result screens
    const oldVote = document.getElementById("voteContainer");
    if (oldVote) oldVote.remove();
    const oldRole = document.querySelector('.role-card');
    if (oldRole) oldRole.remove();
    // Create voting card for remaining players
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

  socket.on("chameleon_lost", (data) => {
    document.body.innerHTML = "";
    const loseDiv = document.createElement("div");
    loseDiv.style.background = "#fff";
    loseDiv.style.borderRadius = "0.5rem";
    loseDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    loseDiv.style.padding = "1.2rem 1rem";
    loseDiv.style.maxWidth = "300px";
    loseDiv.style.width = "100%";
    loseDiv.style.textAlign = "center";
    loseDiv.style.margin = "40px auto";
    loseDiv.style.border = "1px solid #e0e0e0";
    loseDiv.innerHTML = `<h2 style='color:#1a237e; font-size:1.2rem;'>Chameleonas buvo sugautas!</h2><p style='color:#3949ab;'>Chameleonas buvo: <b>${data.chameleon}</b></p>`;
    document.body.appendChild(loseDiv);
  });

  socket.on("discussion_timer", (data) => {
    // Remove any previous voting/result screens
    const oldVote = document.getElementById("voteContainer");
    if (oldVote) oldVote.remove();
    const oldRole = document.querySelector('.role-card');
    if (oldRole) oldRole.remove();
    const oldTie = document.getElementById("tieDiv");
    if (oldTie) oldTie.remove();
    // Show discussion timer
    const discussionDiv = document.createElement("div");
    discussionDiv.id = "discussionDiv";
    discussionDiv.style.background = "#fff";
    discussionDiv.style.borderRadius = "0.5rem";
    discussionDiv.style.boxShadow = "0 1px 4px rgba(0,0,0,0.05)";
    discussionDiv.style.padding = "1.2rem 1rem";
    discussionDiv.style.maxWidth = "300px";
    discussionDiv.style.width = "100%";
    discussionDiv.style.textAlign = "center";
    discussionDiv.style.margin = "40px auto";
    discussionDiv.style.border = "1px solid #e0e0e0";
    discussionDiv.innerHTML = `<h3 style='color:#1a237e; font-size:1.1rem; margin-bottom:1rem;'>Diskusija: kas yra Chameleonas?</h3><div id='discussionTimer'>${data.seconds}</div>`;
    document.body.appendChild(discussionDiv);
    let timeLeft = data.seconds;
    const timer = document.getElementById("discussionTimer");
    const discussionCountdown = setInterval(() => {
      timeLeft--;
      timer.innerText = timeLeft;
      if (timeLeft <= 0) {
        clearInterval(discussionCountdown);
        discussionDiv.innerHTML = "<h3 style='color:#1a237e;'>Balsavimas prasideda!</h3>";
        // Fallback: request voting round if server event is missed
        setTimeout(() => {
          if (!document.getElementById("voteContainer")) {
            socket.emit("request_player_list");
          }
        }, 1200);
      }
    }, 1000);
  });
};
