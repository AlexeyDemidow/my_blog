$(document).on('click', '.like-btn, .modal-like-btn', function (event) {
    event.preventDefault();

    const btn = $(this);
    const postId = btn.data('post-id');

    $.ajax({
        url: `/posts/like_unlike/${postId}/`,
        type: 'POST',
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': getCookie('csrftoken')
        },
        success: function(data) {
            // обновляем количество лайков
            $('#like-actual-' + postId).html(data.like_count);
            $('#modal-like-count').html(data.like_count);

            // переключаем иконку
            const iconHtml = data.is_liked
                ? '<i class="fa-solid fa-heart" style="color:red;"></i>'
                : '<i class="fa-regular fa-heart"></i>';

            // 🔥 Обновляем ВСЕ кнопки лайка этого поста (и модальные, и обычные)
            $(`.like-btn[data-post-id="${postId}"]`).html(iconHtml);
            $(`.modal-like-btn[data-post-id="${postId}"]`).html(iconHtml);
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


