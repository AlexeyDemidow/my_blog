document.addEventListener('DOMContentLoaded', function() {

window.UNREAD_CHATS = JSON.parse(localStorage.getItem('UNREAD_CHATS')) || {};

function updateHeaderDot() {
    const dot = document.getElementById('chat-unread-indicator');
    const hasUnread = Object.values(window.UNREAD_CHATS).some(count => count > 0);
    dot.style.display = hasUnread ? 'block' : 'none';
}

updateHeaderDot();

const chatSocket = new WebSocket(
    (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/chat_list/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatItem = document.querySelector(`.chat-item[data-dialog-id="${data.dialog_id}"]`);
    if (!chatItem) return;
    const preview = chatItem.querySelector('.chat-preview');

    if (data.type === 'messages_read') {
        const badge = chatItem.querySelector('.unread-badge');
        if (badge) badge.remove();
        const dot = chatItem.querySelector('.online-dot');
        if (dot) dot.remove();
        const status = preview.querySelector('.read-status');
        if (status) status.textContent = '✔✔';
        delete window.UNREAD_CHATS[data.dialog_id];
        localStorage.setItem('UNREAD_CHATS', JSON.stringify(window.UNREAD_CHATS));
        updateHeaderDot();
        return;
    }

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

    if (data.type === 'new_message') {
        window.UNREAD_CHATS[data.dialog_id] = (window.UNREAD_CHATS[data.dialog_id] || 0) + 1;
        localStorage.setItem('UNREAD_CHATS', JSON.stringify(window.UNREAD_CHATS));
        updateHeaderDot();

        const text = `${data.sender_username}: ${data.message}`;
        preview.textContent = text;
        preview.dataset.lastMessage = text;
        preview.classList.remove('typing');

        chatItem.parentNode.prepend(chatItem);
    }
};

document.querySelectorAll('.pin-btn').forEach(btn => {
    btn.addEventListener('click', e => {
        e.stopPropagation();
        const url = btn.dataset.url; // используем data-url
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken }
        })
        .then(r => r.json())
        .then(data => {
            btn.textContent = data.is_pinned ? '📌' : '📍';
            const chatItem = btn.closest('.chat-item');
            if (chatItem) document.querySelector('.chat-list').prepend(chatItem);
        })
        .catch(err => console.error(err));
    });
})
});

