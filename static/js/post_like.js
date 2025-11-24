$(document).ready(function() {
    const csrf = getCookie('csrftoken');

    $('.like-btn').on('click', function(event) {
        event.preventDefault();

        const btn = $(this);
        const postId = btn.data('post-id');

        $.ajax({
            url: `/posts/like_unlike/${postId}/`,
            type: 'POST',
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken': csrf
            },
            success: function(data) {

                // обновляем количество лайков
                $('#like-actual-' + postId).html(data.like_count);

                // переключаем текст кнопки
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
