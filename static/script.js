document.addEventListener('DOMContentLoaded', function () {
    var chatBox = document.getElementById('chat-box');
    var userInput = document.getElementById('user-input');
    var sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', function () {
        sendMessage();
    });

    userInput.addEventListener('keyup', function (event) {
        if (event.keyCode === 13) {
            sendMessage();
        }
    });

    function sendMessage() {
        var userMessage = userInput.value;
        if (!userMessage.trim()) {
            return;
        }
        userInput.value = '';
        chatBox.innerHTML += '<div class="message"><i class="fas fa-user user-icon"></i><strong>Você:</strong> ' + userMessage + '</div>';
        sendUserMessage(userMessage);
    }

    function sendUserMessage(message) {
        fetch('/chat', {
            method: 'POST',
            body: new URLSearchParams({
                'user_message': message
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            }
        })
            .then(response => response.json())
            .then(data => {
                var botMessage = data.bot_message;
                chatBox.innerHTML += '<div class="message"><i class="fas fa-robot bot-icon"></i><strong>Bot:</strong>  ' + botMessage + '</div>';
                chatBox.scrollTop = chatBox.scrollHeight;
            });
    }
});
