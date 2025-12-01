$(document).on('click', '.modal-comment-like-btn', function(event) {

    const csrf = getCookie('csrftoken');

    event.preventDefault();

    const btn = $(this);
    const commentId = btn.data('comment-id');

    $.ajax({
        url: `/posts/like_unlike_comment/${commentId}/`,
        type: 'POST',
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': csrf
        },
        success: function(data) {

            // обновляем количество лайков
            $('#modal-actual-comment-like-' + commentId).text(data.like_count);
            // переключаем иконку
            const iconHtml = data.is_liked
                ? '<i class="fa-solid fa-heart" style="color:red;"></i>'
                : '<i class="fa-regular fa-heart"></i>';

            $(`.modal-comment-like-btn[data-comment-id="${commentId}"]`).html(iconHtml);

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
