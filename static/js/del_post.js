$(document).on('click', '.del-post-btn', function(event) {
    event.preventDefault();
    const postId = $(this).data('post-id');
    const csrf = getCookie('csrftoken');

    $.ajax({
        url: `/posts/delete/${postId}/`,
        type: 'POST',
        dataType: 'json',
        data: { 'csrfmiddlewaretoken': csrf },
        success: function(data) {
            if (data.status === 'success') {
                // Удаляем комментарий без перезагрузки
                $(`#post-item-${postId}`).remove();
            } else {
                alert('Ошибка удаления поста');
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
