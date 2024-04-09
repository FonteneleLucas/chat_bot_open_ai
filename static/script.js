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

$(document).ready(function () {
    $('#send-upload').click(function (event) {
        event.preventDefault();
        var resumo = $('#resumo').val();
        var url = $('#url').val();
        var conteudo = $('#conteudo').val();

        $.ajax({
            type: 'POST',
            url: '/extrair',
            data: { url: url, resumo: resumo, conteudo: conteudo },
            success: function (response) {
                if (response.status === 'sucesso') {
                    $('#text-result').html('<p style="color: green;">' + response.mensagem + '</p>');
                } else {
                    $('#text-result').html('<p style="color: red;">' + response.mensagem + '</p>');
                }
            },
            error: function () {
                $('#text-result').html('<p style="color: red;">Erro ao enviar solicitação.</p>');
            }
        });
    });
});