document
  .getElementById("run-sherlock-btn")
  .addEventListener("click", async () => {
    const username = document.getElementById("username").value;
    const nsfw = document.getElementById("nsfw").checked;
    const errorMessage = document.getElementById("error-message");

    errorMessage.textContent = ""; // Clear previous errors

    if (!username.trim()) {
      errorMessage.textContent = "Please enter a username.";
      return;
    }

    try {
      const response = await fetch("/sherlock/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, nsfw }),
        credentials: "include", // Ensures cookies are sent
      });

      if (response.ok) {
        window.location.href = "/sherlock/run"; // Redirect without exposing session ID
      } else {
        const error = await response.json();
        errorMessage.textContent = `[API] Error: ${error.error}`;
      }
    } catch (error) {
      errorMessage.textContent = "Network error, please try again.";
    }
  });
