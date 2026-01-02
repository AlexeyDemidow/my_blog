$(document).on('click', '.message-like-btn', function(event) {

    const csrf = getCookie('csrftoken');

    event.preventDefault();

    const btn = $(this);
    const messageId = btn.data('message-id');

    $.ajax({
        url: `/chat/like_unlike_message/${messageId}/`,
        type: 'POST',
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': csrf
        },
        success: function(data) {

            // обновляем количество лайков
            $('#actual-message-like-' + messageId).text(data.like_count);
            // переключаем иконку
            const iconHtml = data.is_liked
                ? '<i class="fa-solid fa-heart" style="color:red;"></i>'
                : '<i class="fa-regular fa-heart"></i>';

            $(`.message-like-btn[data-message-id="${messageId}"]`).html(iconHtml);

        },
        error: function(error) {
            console.error(error);
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
