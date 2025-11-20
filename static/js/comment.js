$(document).ready(function() {
    // функция для получения CSRF из cookie (если вы не вставляете токен в HTML)
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    const csrftoken = getCookie('csrftoken');

    // Универсальный обработчик для всех кнопок комментариев
    $('.comment-btn').on('click', function(event) {
        event.preventDefault();

        const btn = $(this);
        const postId = btn.data('post-id');

        // Находим элемент textarea по postId
        const textarea = $('#comment-text-' + postId);
        if (!textarea.length) {
            console.error('Textarea not found for post', postId);
            return;
        }

        const text = textarea.val().trim(); // !! ВАЖНО: .val(), а не сам объект
        if (!text) {
            alert('Комментарий пустой');
            return;
        }

        // Блокируем кнопку, чтобы предотвратить повторные клики
        btn.prop('disabled', true);

        $.ajax({
            url: `/posts/add_comment/${postId}/`,
            type: 'POST',
            dataType: 'json',
            data: {
                text: text
            },
            beforeSend: function(xhr, settings) {
                // Передаём CSRF в заголовке — рекомендованный способ
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function(data) {
                if (data.status === 'success') {
                    const c = data.comment;

                    // Создаём DOM-элемент комментария (можно настроить шаблон)
                    const commentHtml = `
                        <li id="comment-${c.id}">
                            <strong>${escapeHtml(c.user)}</strong>:
                            <span class="comment-text">${escapeHtml(c.text)}</span>
                            <small class="text-muted">${escapeHtml(c.created_at)}</small>
                            <button class="del-comment-btn" data-comment-id="${c.id}">${escapeHtml('Удалить')}</button>
                        </li>
                    `;

                    // Добавляем комментарий в начало/конец списка
                    $('#comments-list-' + postId).prepend(commentHtml);

                    // Очищаем поле ввода
                    textarea.val('');
                } else {
                    console.error('Unexpected response', data);
                    alert('Ошибка при добавлении комментария');
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error, xhr.responseText);
                alert('Не удалось отправить комментарий. Попробуйте позже.');
            },
            complete: function() {
                // Разблокируем кнопку в любом случае
                btn.prop('disabled', false);
            }
        });
    });

    // Простая функция экранирования чтобы избежать XSS в выводе (сервер тоже должен валидировать!)
    function escapeHtml(string) {
        if (!string) return '';
        return String(string)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
