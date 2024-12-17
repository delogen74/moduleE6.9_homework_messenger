const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/' + chatId + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const messagesDiv = document.getElementById('messages');
    const newMessage = document.createElement('p');
    newMessage.innerHTML = `<strong>${data.sender}:</strong> ${data.message}`;
    messagesDiv.appendChild(newMessage);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.getElementById('messageForm').onsubmit = function(e) {
    e.preventDefault();
    const messageInputDom = document.getElementById('messageInput');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    messageInputDom.value = '';
};
