let socket = null;

document.addEventListener('DOMContentLoaded', function() {

    const dialogId = window.DIALOG_ID;
    const currentUser = window.CURRENT_USER_ID;

    socket = new WebSocket(
        (window.location.protocol === 'https:' ? 'wss://' : 'ws://')
        + window.location.host
        + '/ws/chat/' + dialogId + '/'
    );

    const messagesDiv = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    let typingTimer = null;

    socket.onopen = function () {
        tryMarkAsRead();

        if (window.UNREAD_CHATS) {
            delete window.UNREAD_CHATS[dialogId];
            localStorage.setItem('UNREAD_CHATS', JSON.stringify(window.UNREAD_CHATS));
            if (typeof updateHeaderDot === 'function') updateHeaderDot();
        }
    };

        // Клик на кнопку удаления
    $(document).on('click', '.del-message-btn', function (e) {
        e.preventDefault();

        const messageId = $(this).data('message-id');

        if (!confirm("Вы уверены, что хотите удалить сообщение?")) return;

        socket.send(JSON.stringify({
            type: "delete_message",
            message_id: messageId
        }));
    });

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

    // -------- edit message --------
        if (data.type === "message_edited") {
            const messageDiv = document.querySelector(
                `.message[data-id="${data.message_id}"]`
            );
            if (!messageDiv) return;

            const textDiv = messageDiv.querySelector(".text");
            textDiv.innerHTML = `
                ${data.text}
                <span class="chat-time">отредактировано</span>
            `;
            return;
        }

        if (data.type === "message_deleted") {
            const messageDiv = document.querySelector(`.message[data-id="${data.message_id}"]`);
            if (messageDiv) messageDiv.remove();
            return;
        }

        // -------- typing --------
        if (data.type === 'typing' && data.username !== currentUser) {
            typingIndicator.textContent = data.is_typing
                ? `${data.username} печатает...`
                : '';
            return;
        }

    // -------- read --------
        if (data.type === 'messages_read' && data.message_ids) {
            data.message_ids.forEach(id => {
                const msg = document.querySelector(
                    `.message.me[data-id="${id}"] .read-status`
                );
                if (msg) msg.textContent = '✔✔';
            });
            return;
        }

        // -------- like --------
        if (data.type === 'like_update') {
            const messageId = data.message_id;
            console.log(window.CURRENT_USER_ID)
            console.log(data.username)
            // обновляем счётчик ВСЕМ
            $('#actual-message-like-' + messageId).text(data.like_count);

            // обновляем сердце ТОЛЬКО себе
            if (data.username === window.CURRENT_USER_ID) {
                const iconHtml = data.is_liked
                    ? '<i class="fa-solid fa-heart" style="color:red;"></i>'
                    : '<i class="fa-regular fa-heart"></i>';

                $(`.message-like-btn[data-message-id="${messageId}"]`)
                    .html(iconHtml);
            }

            return;
        }

        // -------- message --------
        if (data.message) {
            typingIndicator.textContent = '';
            addMessage(data.sender, data.message, data.id);
            setTimeout(tryMarkAsRead, 0);
        }
    };

    initEditMessages(socket);

    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
    });


    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        socket.send(JSON.stringify({
            type: 'message',
            message: text
        }));
        input.value = '';
    }

    sendBtn.addEventListener('click', sendMessage);

    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // ⛔ перенос строки
            sendMessage();
        }
    });


    input.addEventListener('input', () => {
        socket.send(JSON.stringify({type: 'typing', is_typing: true}));

        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            socket.send(JSON.stringify({type: 'typing', is_typing: false}));
        }, 1200);
    });

    function addMessage(sender, message, id) {
        const div = document.createElement('div');
        div.classList.add('message');
        div.dataset.id = id;
        readSent = false;
        setTimeout(tryMarkAsRead, 0);

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

    const emojiBtn = document.getElementById('emoji-btn');
    const emojiPanel = document.getElementById('emoji-panel');
    const messageInput = document.getElementById('message-input');

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


    let windowFocused = true;
    let readSent = false;

    document.addEventListener('visibilitychange', () => {
        windowFocused = !document.hidden;
        tryMarkAsRead();
    });

    function isScrolledToBottom() {
        const threshold = 40;
        return (
            messagesDiv.scrollHeight
            - messagesDiv.scrollTop
            - messagesDiv.clientHeight
        ) < threshold;
    }

    messagesDiv.addEventListener('scroll', tryMarkAsRead);

    function tryMarkAsRead() {
        if (!windowFocused) return;
        if (!isScrolledToBottom()) return;
        if (readSent) return;

        socket.send(JSON.stringify({
            type: 'messages_read',
            dialog_id: dialogId
        }));
        readSent = true;
    }

    let dialogInFocus = document.visibilityState === 'visible';

    document.addEventListener('visibilitychange', () => {
        dialogInFocus = document.visibilityState === 'visible';

        if (dialogInFocus) {
            tryMarkAsRead();
        }
    });

    window.addEventListener('beforeunload', () => {
        readSent = false;
    });


    $(document).on('click', '.message-like-btn', function (e) {
        e.preventDefault();

        const messageId = $(this).data('message-id');

        socket.send(JSON.stringify({
            type: 'toggle_like',
            message_id: messageId
        }));
    });

    let page = 1;
    let loading = false;
    let hasNext = true;

    messagesDiv.addEventListener('scroll', () => {
        if (messagesDiv.scrollTop === 0 && !loading && hasNext) {
            loadMoreMessages();
        }
    });

    function loadMoreMessages() {
        loading = true;
        page++;

        const oldHeight = messagesDiv.scrollHeight;

        fetch(`/chat/dialog/${dialogId}/messages/?page=${page}`)
            .then(res => res.json())
            .then(data => {
                if (!data.html.trim()) {
                    hasNext = false;
                    return;
                }

                messagesDiv.insertAdjacentHTML('afterbegin', data.html);

                const newHeight = messagesDiv.scrollHeight;
                messagesDiv.scrollTop = newHeight - oldHeight;

                hasNext = data.has_next;
            })
            .finally(() => {
                loading = false;
            });
    }
})


