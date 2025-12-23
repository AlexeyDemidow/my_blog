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
