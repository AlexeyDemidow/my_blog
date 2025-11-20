$(document).on('click', '.del-comment-btn', function(event) {
    event.preventDefault();
    const commentId = $(this).data('comment-id');
    const csrf = getCookie('csrftoken');

    $.ajax({
        url: `/posts/del_comment/${commentId}/`,
        type: 'POST',
        dataType: 'json',
        data: { 'csrfmiddlewaretoken': csrf },
        success: function(data) {
            if (data.status === 'success') {
                // Удаляем комментарий без перезагрузки
                $(`#comment-${commentId}`).remove();
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
