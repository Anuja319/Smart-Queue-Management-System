async function loadCurrentToken() {
  try {
    const response = await fetch("http://localhost:8000/api/current");

    const data = await response.json();

    console.log("Current token response:", data);

    const tokenElement = document.getElementById("currentToken");

    const counterElement = document.getElementById("counterNumber");

    const messageElement = document.getElementById("displayMessage");

    if (data.current && data.current.token_id !== null) {
      const token = data.current.token_id;

      tokenElement.textContent = "A" + String(token).padStart(3, "0");

      counterElement.textContent = "Counter 1";

      messageElement.textContent = "Please proceed to the counter.";
    } else {
      tokenElement.textContent = "---";

      counterElement.textContent = "Counter 1";

      messageElement.textContent = "Please wait for your token to be called.";
    }
  } catch (error) {
    console.error("Unable to load current token:", error);
  }
}

loadCurrentToken();

setInterval(loadCurrentToken, 3000);
