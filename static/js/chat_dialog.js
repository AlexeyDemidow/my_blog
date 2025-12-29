document.addEventListener('DOMContentLoaded', function() {

    const dialogId = window.DIALOG_ID;
    const currentUser = window.CURRENT_USER_ID;

    const messagesDiv = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    const emojiBtn = document.getElementById('emoji-btn');
    const emojiPanel = document.getElementById('emoji-panel');
    const messageInput = document.getElementById('message-input');



    const socket = new WebSocket(
        (window.location.protocol === 'https:' ? 'wss://' : 'ws://')
        + window.location.host
        + '/ws/chat/' + dialogId + '/'
    );



    let typingTimer = null;

    socket.onopen = function() {
        socket.send(JSON.stringify({
            type: 'messages_read',
            dialog_id: dialogId
        }));

        if (window.UNREAD_CHATS) {
            delete window.UNREAD_CHATS[dialogId];
            localStorage.setItem('UNREAD_CHATS', JSON.stringify(window.UNREAD_CHATS));
            if (typeof updateHeaderDot === 'function') updateHeaderDot();
        }
    }

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data.type === 'typing' && data.username !== currentUser) {
            typingIndicator.textContent = data.is_typing
                ? `${data.username} печатает...`
                : '';
            return;
        }

        if (data.type === 'messages_read') {
            document.querySelectorAll('.message.me .read-status').forEach(el => {
                el.textContent = '✔✔';
            });
            return;
        }

        if (data.message) {
            typingIndicator.textContent = '';
            addMessage(data.sender, data.message);
        }
    };

    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        socket.send(JSON.stringify({ message: text }));
        input.value = '';
    }

    sendBtn.onclick = sendMessage;

    input.addEventListener('keydown', e => {
        if (e.key === 'Enter') sendMessage();
    });

    input.addEventListener('input', () => {
        socket.send(JSON.stringify({ type: 'typing', is_typing: true }));

        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            socket.send(JSON.stringify({ type: 'typing', is_typing: false }));
        }, 1200);
    });

    function addMessage(sender, message) {
        const div = document.createElement('div');
        div.classList.add('message');

        let readStatus = '';

        if (sender === currentUser) {
            div.classList.add('me');
            readStatus = `<span class="read-status">✔</span>`;
        }

        div.innerHTML = `
            <div class="text">
                ${message}
                ${readStatus}
            </div>
        `;

        messagesDiv.appendChild(div);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function scrollToBottom() {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    scrollToBottom();




    emojiBtn.addEventListener('click', () => {
        emojiPanel.style.display = emojiPanel.style.display === 'none' ? 'block' : 'none';
    });

    emojiPanel.querySelectorAll('.emoji').forEach(el => {
        el.addEventListener('click', () => {
            messageInput.value += el.textContent;
            messageInput.focus();
        });
    });

    // Закрытие панели при клике вне её
    document.addEventListener('click', (e) => {
        if (!emojiPanel.contains(e.target) && e.target !== emojiBtn) {
            emojiPanel.style.display = 'none';
        }
    });
});
