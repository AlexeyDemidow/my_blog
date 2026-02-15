$(document).on('click', '.del-message-btn', function(event) {
    event.preventDefault();
    event.stopPropagation(); // ОБЯЗАТЕЛЬНО

    const btn = $(this); // ← СОХРАНЯЕМ
    const messageId = $(this).data('message-id');
    const csrf = getCookie('csrftoken');

    $.ajax({
        url: `/chat/delete_message/${messageId}/`,
        type: 'POST',
        dataType: 'json',
        data: { 'csrfmiddlewaretoken': csrf },
        success: function(data) {
            if (data.status === 'success') {
                btn.closest('.message').remove();

            } else {
                alert('Ошибка удаления комментария');
            }
        },
        error: function(err) {
            console.error(err);
        }
    });
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    }
});

document.addEventListener('click', function (e) {
    const btn = e.target.closest('.options-btn');

    document.querySelectorAll('.message-options-menu')
        .forEach(menu => menu.classList.remove('active'));

    if (btn) {
        e.stopPropagation();
        btn.parentElement.classList.add('active');
    }
});