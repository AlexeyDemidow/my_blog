$(document).on('click', '.repost-btn, .modal-repost-btn', function() {
    const postId = $(this).data('post-id');

    $.ajax({
        url: `/posts/repost/${postId}/`,
        type: 'POST',
        data: { 'csrfmiddlewaretoken': getCookie('csrftoken') },
        success: function(data) {
            if (data.status === 'success') {
                // увеличиваем число репостов
                let counter = $('#repost-count-' + postId);
                let modalcounter = $('#modal-repost-count-' + postId);
                counter.text( parseInt(counter.text()) + 1 );
                modalcounter.text( parseInt(modalcounter.text()) + 1 );
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
