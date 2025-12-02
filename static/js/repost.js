let repostPostId = null; // пост, который будем репостить

$(document).on('click', '.repost-btn, .modal-repost-btn', function() {
    repostPostId = $(this).data('post-id');

    // показываем окно ввода текста
    $('#repost-popup').show();
});

// --- кнопка "Отмена" ---
$(document).on('click', '#repost-cancel', function() {
    $('#repost-popup').hide();
    $('#repost-text').val('');
});

// --- кнопка "Репостнуть" ---
$(document).on('click', '#repost-send', function() {
    const text = $('#repost-text').val();

    $.ajax({
        url: `/posts/repost/${repostPostId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': getCookie('csrftoken'),
            'text': text  // ← отправляем подпись
        },
        success: function(data) {
            if (data.status === 'success') {
                // обновляем оба счётчика
                let counter = $('#repost-count-' + repostPostId);
                let modalcounter = $('#modal-repost-count-' + repostPostId);

                counter.text(parseInt(counter.text()) + 1);
                modalcounter.text(parseInt(modalcounter.text()) + 1);
            }

            // закрываем окно
            $('#repost-popup').hide();
            $('#repost-text').val('');
        },
        error: function(err) {
            console.error(err);
        }
    });
});

// CSRF
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
