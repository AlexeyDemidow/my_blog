document.addEventListener('DOMContentLoaded', function() {
    const socket = new WebSocket(
        (location.protocol === 'https:' ? 'wss://' : 'ws://')
        + location.host + '/ws/chat_list/'
    );

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        const chatItem = document.querySelector(
            `.chat-item[data-dialog-id="${data.dialog_id}"]`
        );
        if (!chatItem) return;

        const preview = chatItem.querySelector('.chat-preview');

        /* =======================
           ✔✔ ПРОЧИТАНО
        ======================= */
        if (data.type === 'messages_read') {

            // удаляем badge
            const badge = chatItem.querySelector('.unread-badge');
            if (badge) badge.remove();

            // удаляем точку (dot)
            const dot = chatItem.querySelector('.online-dot');
            if (dot) dot.remove();

            // меняем ✔ → ✔✔ в превью, если сообщение своё
            const status = preview.querySelector('.read-status');
            if (status) {
                status.textContent = '✔✔';
            }
            return;
        }

        /* =======================
           ✍️ TYPING
        ======================= */
        if (data.type === 'chat_typing') {
            if (data.is_typing) {
                preview.textContent = 'печатает…';
                preview.classList.add('typing');
            } else {
                preview.textContent = preview.dataset.lastMessage || '';
                preview.classList.remove('typing');
            }
            return;
        }

        /* =======================
           ✉️ NEW MESSAGE
        ======================= */
        if (data.type === 'new_message') {

            // badge
            let badge = chatItem.querySelector('.unread-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'unread-badge';
                badge.textContent = '1';
                chatItem.querySelector('.chat-header').appendChild(badge);
            } else {
                badge.textContent = parseInt(badge.textContent) + 1;
            }

            // превью
            const text = `${data.sender}: ${data.message}`;
            preview.textContent = text;
            preview.dataset.lastMessage = text;
            preview.classList.remove('typing');

            // поднимаем чат
            chatItem.parentNode.prepend(chatItem);
        }
    };

    document.querySelectorAll('.pin-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();

            const url = btn.dataset.pinUrl;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.CSRF_TOKEN
                }
            })
            .then(r => r.json())
            .then(data => {
                btn.textContent = data.is_pinned ? '📌' : '📍';

                const chatItem = btn.closest('.chat-item');
                document.querySelector('.chat-list').prepend(chatItem);
            });
        });
    });
});

