const messageInput =
    document.getElementById("messageInput");

const chatMessages =
    document.getElementById("chatMessages");

const sendButton =
    document.getElementById("sendButton");


messageInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();
        }
    }
);


function addMessage(
    text,
    type,
    agent = null
) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add(
        "message",
        type === "user"
            ? "user-message"
            : "bot-message"
    );


    const label =
        document.createElement("div");

    label.classList.add(
        "message-label"
    );

    label.textContent =
        type === "user"
            ? "You"
            : "TechStore AI";


    const content =
        document.createElement("div");

    content.classList.add(
        "message-content"
    );

    content.textContent = text;


    messageDiv.appendChild(
        label
    );

    messageDiv.appendChild(
        content
    );


    if (agent) {

        const agentLabel =
            document.createElement("div");

        agentLabel.classList.add(
            "agent-name"
        );

        agentLabel.textContent =
            `Handled by: ${agent}`;

        messageDiv.appendChild(
            agentLabel
        );
    }


    chatMessages.appendChild(
        messageDiv
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    return messageDiv;
}


function showTypingIndicator() {

    const typingDiv =
        document.createElement("div");

    typingDiv.classList.add(
        "message",
        "bot-message"
    );

    typingDiv.id =
        "typingIndicator";


    const label =
        document.createElement("div");

    label.classList.add(
        "message-label"
    );

    label.textContent =
        "TechStore AI";


    const content =
        document.createElement("div");

    content.classList.add(
        "message-content",
        "typing"
    );

    content.textContent =
        "Thinking...";


    typingDiv.appendChild(
        label
    );

    typingDiv.appendChild(
        content
    );


    chatMessages.appendChild(
        typingDiv
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function removeTypingIndicator() {

    const typing =
        document.getElementById(
            "typingIndicator"
        );

    if (typing) {
        typing.remove();
    }
}


async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {
        return;
    }


    addMessage(
        message,
        "user"
    );


    messageInput.value = "";

    messageInput.disabled = true;

    sendButton.disabled = true;


    showTypingIndicator();


    try {

        const response = await fetch(
            "/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    {
                        message: message
                    }
                )
            }
        );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );
        }


        const data =
            await response.json();


        removeTypingIndicator();


        addMessage(
            data.answer,
            "bot",
            data.agent
        );

    }

    catch (error) {

        removeTypingIndicator();


        const errorMessage =
            addMessage(
                "Sorry, I could not process your request.",
                "bot"
            );

        errorMessage.classList.add(
            "error-message"
        );


        console.error(
            error
        );
    }

    finally {

        messageInput.disabled = false;

        sendButton.disabled = false;

        messageInput.focus();
    }
}


function sendSuggestion(message) {

    messageInput.value =
        message;

    sendMessage();
}