document.addEventListener("DOMContentLoaded", function () {
    const chatbox = document.getElementById("chatbox");
    const chatBody = document.getElementById("chat-body");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatBtn = document.getElementById("chatbot-btn");
    const closeChat = document.getElementById("close-chat");

    chatBtn.addEventListener("click", function () {
        chatbox.classList.toggle("hidden");
    });

    closeChat.addEventListener("click", function () {
        chatbox.classList.add("hidden");
    });

    sendBtn.addEventListener("click", function () {
        sendMessage();
    });

    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    function sendMessage() {
        let message = userInput.value.trim();
        if (message === "") return;

        // Append user message
        appendMessage("You", message);
        userInput.value = "";

        // Send message to the backend
        fetch("/chat", {
            method: "POST",
            body: JSON.stringify({ message: message }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => {
            appendMessage("Bot", data.response);
        })
        .catch(error => {
            console.error("Error:", error);
            appendMessage("Bot", "Error: Could not connect to the server.");
        });
    }

    function appendMessage(sender, message) {
        let messageElement = document.createElement("p");
        messageElement.classList.add(sender === "You" ? "user-message" : "bot-message");
        messageElement.textContent = `${sender}: ${message}`;
        chatBody.appendChild(messageElement);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
});

