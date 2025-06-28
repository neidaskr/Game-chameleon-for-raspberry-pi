const socket = io();

let hasJoined = false;

const lobbyDiv = document.getElementById("lobby");
const nameInput = document.getElementById("nameInput");
const joinButton = document.getElementById("joinButton");

joinButton.addEventListener("click", () => {
  const playerName = nameInput.value.trim();
  if (!playerName) {
    alert("Please enter your name");
    return;
  }
  socket.emit("join", { name: playerName });
  hasJoined = true;
  joinButton.disabled = true;
  nameInput.disabled = true;
});

// Handle the game start data (role, word)
socket.on("game_data", (data) => {
  if (!hasJoined) return; // Ignore if not joined

  lobbyDiv.style.display = "none";

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

  // Tell server this client is ready
  socket.emit("client_ready");
});

// Start the countdown timer when server says to start
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
        socket.emit("request_player_list"); // Request voting list
      }
    }, 1000);
  }, 10000);
});

// Show voting buttons
socket.on("player_list", (data) => {
  if (!hasJoined) return;

  // Remove old voting UI if any
  const oldVoteContainer = document.getElementById("voteContainer");
  if (oldVoteContainer) oldVoteContainer.remove();

  const voteContainer = document.createElement("div");
  voteContainer.id = "voteContainer";
  voteContainer.style.textAlign = "center";
  voteContainer.style.marginTop = "20px";
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

// Show voting results
socket.on("voting_result", (data) => {
  if (!hasJoined) return;

  // Remove old vote UI
  const voteContainer = document.getElementById("voteContainer");
  if (voteContainer) voteContainer.remove();

  const resultDiv = document.createElement("div");
  resultDiv.style.textAlign = "center";
  resultDiv.style.marginTop = "20px";
  resultDiv.innerHTML = "<h3>Voting Results:</h3>";

  for (const [voter, voted] of Object.entries(data.votes)) {
    const line = document.createElement("p");
    line.innerText = `${voter} voted for ${voted}`;
    resultDiv.appendChild(line);
  }

  document.body.appendChild(resultDiv);
});
