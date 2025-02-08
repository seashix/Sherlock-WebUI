if (!sessionId || sessionId === "None") {
  document.getElementById("session-id").textContent =
    "Session not found. Please restart the search.";
  console.error("Session ID is missing.");
} else {
  document.getElementById(
    "session-id"
  ).textContent = `Session ID: ${sessionId}`;
}

if (!username || username === "None") {
  document.getElementById("username").textContent =
    "Username not found. Please restart the search.";
  console.error("Username is missing.");
} else {
  document.getElementById("username").textContent = `Username: ${username}`;
}

// Connect to WebSocket
const socket = io({ transports: ["websocket"] }); // Force WebSocket mode

socket.on("connect", () => {
  console.log(`[SocketIO] Connected to session: ${sessionId}`);
  socket.emit("join", { room: `${sessionId}` });
});

let firstLogReceived = false; // To track the first log line
let logsContent = ""; // Store logs for download

socket.on("log", (data) => {
  const logsDiv = document.getElementById("logs");
  const tagInfos = '<span style="color: yellow;">[INFOS]</span>';
  const tagFound = '<span style="color: green;">[FOUND]</span>';
  const tagError = '<span style="color: red;">[ERROR]</span>';

  // Remove "Waiting for logs..." when first log appears
  if (!firstLogReceived) {
    logsDiv.innerHTML = ""; // Clear the placeholder text
    logsContent += "---- Sherlock WebUI Project ----\n";
    logsContent += `Session ID for ${username} is ${sessionId}\n`;
    //logsContent += "[+] is for found, [*] is for information\n\n";
    logsContent += "---- See logs for your output ----\n";
    firstLogReceived = true;
  }

  let logLine = data.data;
  logsContent +=
    logLine.replace(/\[\*\]/g, tagInfos).replace(/\[\+\]/g, tagFound) + "\n"; // Store log for downloading

  // Apply colors to logs dynamically
  logLine = logLine.replace(/\[\*\]/g, tagInfos); // Yellow [*]
  logLine = logLine.replace(/\[\+\]/g, tagFound); // Green [+]

  // Highlight search results count in green
  logLine = logLine.replace(
    /Search completed with (\d+) results/,
    (match, num) =>
      `Search completed with <span style="color: green;">${num}</span> results`
  );

  // Convert URLs into clickable links
  logLine = logLine.replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" target="_blank" style="color: cyan; text-decoration: underline;">$1</a>'
  );

  if (logLine.includes(`https://www.youtube.com/@${username}`)) {
    ifYouTubeChannelExist(username).then((exists) => {
      if (exists) {
        logLine = logLine.replace(
          `[+] YouTube: https://www.youtube.com/@${username}`,
          `${tagFound} <a href="https://www.youtube.com/@${username}" target="_blank" style="color: cyan; text-decoration: underline;">https://www.youtube.com/@${username}</a>\n`
        );
      } else {
        logLine = logLine.replace(
          `[+] YouTube: https://www.youtube.com/@${username}`,
          `<span style="display: none;">${tagError} <a href="https://www.youtube.com/@${username}" target="_blank" style="color: cyan; text-decoration: underline;">https://www.youtube.com/@${username}</a></span>`
        );
        logsContent = logsContent.replace(
          `[+] YouTube: https://www.youtube.com/@${username}`,
          "[*] Found false positive (404 error) for YouTube channel, skipping... Fixed by Sherlock WebUI.\n"
        );
        console.log(
          `[DEBUG] YouTube channel does not exist for ${username}, skipping the Sherlock false positive (404 error).`
        );
      }
    });
  }

  const logElement = document.createElement("p");
  logElement.innerHTML = logLine; // Use innerHTML to apply styling
  logsDiv.appendChild(logElement);
  logsDiv.scrollTop = logsDiv.scrollHeight; // Auto-scroll to latest log
});

socket.on("log_done", () => {
  console.log("[SocketIO] Search completed.");

  const logsDiv = document.getElementById("logs");

  // Flashy completion message
  const completionMessage = document.createElement("p");
  completionMessage.innerHTML =
    '<span style="color: orange; font-weight: bold;">--- Search completed! ---</span>';
  logsDiv.appendChild(completionMessage);

  // Add Download Link
  const downloadLink = document.createElement("a");
  downloadLink.href = "#";
  downloadLink.textContent = "Download Logs";
  downloadLink.style =
    "display: block; margin-top: 10px; font-weight: bold; color: white; cursor: pointer; text-decoration: underline;";
  downloadLink.onclick = () => downloadLogs();
  logsDiv.appendChild(downloadLink);
});

// Function to download logs as a file
function downloadLogs() {
  const blob = new Blob([logsContent], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `SherlockWebUI.logs-${sessionId}.txt`;
  link.click();
}

// Function to check if YouTube channel exists because the 404 error is a false positive
function ifYouTubeChannelExist(username) {
  return fetch(`/proxy/youtube?at=${username}`)
    .then((response) => {
      if (response.status === 404) {
        console.log(`[Proxy] YouTube returned 404 for ${username}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log(`[Proxy] Response data:`, data);
      if (data.response === "taken") {
        console.log(`[Proxy] YouTube channel found for ${username}`);
        return true;
      } else if (data.response === "not_taken") {
        console.log(`[Proxy] YouTube channel not found for ${username}`);
        return false;
      } else {
        console.log(`[Proxy] Unexpected response: ${data.response}`);
        return false;
      }
    })
    .catch((error) =>
      console.log("[Proxy] Error checking YouTube page:", error)
    );
}

// Warn user if they try to leave the page
window.addEventListener("beforeunload", (event) => {
  console.log("[SocketIO] Sending disconnect event before leaving.");
  socket.disconnect();

  // Custom alert
  setTimeout(() => {
    alert(
      "The search is ending, and the socket will be closed. See you soon on Sherlock WebUI!"
    );
  }, 10); // Delayed to avoid Chrome overriding it

  // Browser default warning
  event.preventDefault();
  event.returnValue =
    "Are you sure you want to leave? The search will be interrupted.";
});
