$(document).ready(function() {
    const csrf = getCookie('csrftoken');

    $(document).on('click', '.comment-like-btn', function(event) {
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
                $('#actual-comment-like-' + commentId).text(data.like_count);

                // переключаем иконку
                if (data.is_liked) {
                    btn.html('<i class="fa-solid fa-heart" style="color:red;"></i>');
                } else {
                    btn.html('<i class="fa-regular fa-heart"></i>');
                }

            },
            error: function(error) {
                console.error(error);
            }
        });
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
