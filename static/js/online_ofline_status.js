function formatLastSeen(dateString) {
    if (!dateString) return 'оффлайн';

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'оффлайн';

    const diff = Math.floor((Date.now() - date) / 1000);

    if (diff < 60) return 'был(а) только что';
    if (diff < 3600) return `был(а) ${Math.floor(diff / 60)} мин назад`;
    if (diff < 86400) return `был(а) ${Math.floor(diff / 3600)} ч назад`;

    return `был(а) ${date.toLocaleDateString()}`;
}

const onlineSocket = new WebSocket(
    (location.protocol === 'https:' ? 'wss://' : 'ws://')
    + location.host + '/ws/online/'
);

function updateOnlineStatus(userId, isOnline) {
    document
        .querySelectorAll(`[data-user-id="${userId}"]`)
        .forEach(el => {
            el.classList.toggle('online', isOnline);
        });

    if (isOnline) {
        window.ONLINE_USERS.add(userId);
    } else {
        window.ONLINE_USERS.delete(userId);
    }
}

onlineSocket.addEventListener('message', function (e) {
    const data = JSON.parse(e.data);

    // 🔥 ИНИЦИАЛИЗАЦИЯ (САМЫЙ ВАЖНЫЙ МОМЕНТ)
    if (data.type === 'online_users') {
        data.users.forEach(userId => {
            document
                .querySelectorAll(`[data-user-id="${userId}"] .status-text`)
                .forEach(el => el.textContent = 'онлайн');
        });
    }

    if (data.type === 'user_online') {
        document
            .querySelectorAll(`[data-user-id="${data.user_id}"] .status-text`)
            .forEach(el => el.textContent = 'онлайн');
    }

    if (data.type === 'user_offline') {
        document
            .querySelectorAll(`[data-user-id="${data.user_id}"] .status-text`)
            .forEach(el => {
                el.textContent = formatLastSeen(data.last_seen);
            });
    }
});

onlineSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === 'online_users') {
        data.users.forEach(userId => {
            updateOnlineStatus(userId, true);
        });
        return;
    }

    if (data.type === 'user_online') {
        updateOnlineStatus(data.user_id, true);
    }

    if (data.type === 'user_offline') {
        updateOnlineStatus(data.user_id, false);
    }
};

// 🔥 ДЛЯ МОДАЛОК / AJAX
window.syncOnlineStatus = function () {
    document.querySelectorAll('[data-user-id]').forEach(el => {
        const userId = parseInt(el.dataset.userId);
        if (window.ONLINE_USERS.has(userId)) {
            el.classList.add('online');
        }
    });
};

// Функция обновления точки во вкладке
function updateHeaderDot() {
    const dot = document.getElementById('chat-unread-indicator');
    const hasUnread = Object.values(window.UNREAD_CHATS).some(count => count > 0);
    dot.style.display = hasUnread ? 'block' : 'none';
};

// Сразу после загрузки страницы показываем точку, если есть непрочитанные
updateHeaderDot();

// WebSocket для получения новых сообщений
const chatSocket = new WebSocket(
    (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/chat_list/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === 'new_message') {
        // Отмечаем диалог как непрочитанный
        window.UNREAD_CHATS[data.dialog_id] = (window.UNREAD_CHATS[data.dialog_id] || 0) + 1;

        localStorage.setItem('UNREAD_CHATS', JSON.stringify(window.UNREAD_CHATS));
        updateHeaderDot();
    }

    if (data.type === 'messages_read') {
        // Сообщения прочитаны → удаляем метку
        delete window.UNREAD_CHATS[data.dialog_id];
        localStorage.setItem('UNREAD_CHATS', JSON.stringify(window.UNREAD_CHATS));
        updateHeaderDot();
    }
};