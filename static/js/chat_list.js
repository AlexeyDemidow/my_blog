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

            const dialogId = data.dialog_id;

            // Найти диалог в списке
            let dialog = dialogs.find(d => d.id === dialogId);

            if (!dialog) {
                // Если диалога нет (возможно он был скрыт), создаем его
                dialog = {
                    id: dialogId,
                    messages: [],
                    hidden: false
                };
                dialogs.unshift(dialog); // вставляем в начало списка
            }

            // Если пришёл флаг, что диалог был скрыт
            if (data.unhide) {
                dialog.hidden = false;
                // Можно обновить UI, показать диалог в списке
                showDialogInUI(dialog);
            }

            // Добавляем новое сообщение
            dialog.messages.push({
                sender: data.sender,
                text: data.message,
                from_me: data.from_me
            });

            // Обновляем UI
            renderMessages(dialogId);


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

        if (data.type === 'dialog_hidden' || data.type === 'dialog_deleted') {
            const chatItem = document.querySelector(
                `.chat-item[data-dialog-id="${data.dialog_id}"]`
            );
            if (chatItem) chatItem.remove();
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

    document.querySelectorAll('.delete-chat').forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();

            const chatItem = btn.closest('.chat-item');
            const dialogId = chatItem.dataset.dialogId;

            const choice = confirm(
                'ОК — удалить у всех\nОтмена — удалить только у себя'
            );

            socket.send(JSON.stringify({
                type: choice ? 'delete_dialog_all' : 'delete_dialog_me',
                dialog_id: dialogId
            }));
        });
    });

    function showDialogInUI(dialog) {
        const chatList = document.querySelector('.chat-list');

        // Если уже есть элемент в DOM, ничего не делаем
        if (document.querySelector(`.chat-item[data-dialog-id="${dialog.id}"]`)) return;

        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.dataset.dialogId = dialog.id;
        chatItem.innerHTML = `
            <div class="chat-header">${dialog.messages[0]?.sender || ''}</div>
            <div class="chat-preview">${dialog.messages[0]?.text || ''}</div>
        `;

        // Вставляем в начало списка
        chatList.prepend(chatItem);
}


});

