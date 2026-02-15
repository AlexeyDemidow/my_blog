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
                $(`#post-item-${postId}`).remove();

                if (data.original_post_id) {
                    let origId = data.original_post_id;

                    let counter = $('#repost-count-' + origId);
                    let modalcounter = $('#modal-repost-count-' + origId);

                    counter.text(parseInt(counter.text()) - 1);
                    modalcounter.text(parseInt(modalcounter.text()) - 1);
                }

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
