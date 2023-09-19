//Janell Schirtzinger CIS 477  JAVASCRIPT CODE BELOW

document.addEventListener('DOMContentLoaded', function () {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatForm = document.getElementById('chat-form');

    //When user clicks send
    sendButton.addEventListener('click', function () {
        event.preventDefault();
        const userMessage = userInput.value.trim();
        //sendMessage(userMessage)
        //go through message from user until it ends
        if (userMessage !== '') {
            appendMessage('sent', userMessage);
            sendMessage(userMessage)
            userInput.value = '';


        }
    });

    //function to add a new message to the chat interface.
    function appendMessage(type, message) {
        //creating new div element represents the message that is being added to the chat by user
        const messageDiv = document.createElement('div');
        //if type is "user," it will have the class "message user," and if type is "bot," it will have the class "message bot."
        messageDiv.className = `message ${type}`;
        //sets the content of the div element to the text of the message user enters
        messageDiv.textContent = message;
        // adds the message to the chat interface
        chatMessages.appendChild(messageDiv);
        // Scroll to the bottom of the chat window to see full message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }


    function sendMessage() {
    let userInput = document.getElementById("user-input").value;

    // Send the user's message to the Flask backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: userInput })
    })
    .then(response => response.json())
    .then(data => {


        // Append the bot's response to the chat
        console.log("Bot Response:", data.response);

        let chatMessages = document.getElementById("chat-messages");
        let messageElement = document.createElement("div");
        messageElement.className = "message received";
        messageElement.textContent = data.response;
        chatMessages.appendChild(messageElement);

        // Clear the user's input
        document.getElementById("user-input").value = "";


    })
    .catch(error => {
        console.error("Error:", error);
    });
}

});
