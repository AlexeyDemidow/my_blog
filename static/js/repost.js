// Открытие модалки репоста
$(document).on('click', '.repost-btn', function () {
    const postId = $(this).data('post-id');

    // Загружаем данные поста
    $.ajax({
        url: `/posts/get_data_for_repost/${postId}/`,
        type: 'GET',
        success: function (data) {

            let html = `
                <p><strong>@${data.author}</strong></p>
                <p>${data.content}</p>
            `;

            if (data.images.length > 0) {
                data.images.forEach(img => {
                    console.log(img.image)
                    html += `<img src="/media/${img.image}" alt="">`;
                });
            }

            $("#repost-original").html(html);

            // Запоминаем ID поста
            $("#send-repost-btn").data("post-id", postId);

            $("#repostModal").fadeIn(150);
        }
    });
});

// Закрытие модалки
$(document).on('click', '.repost-close', function() {
    $("#repostModal").fadeOut(150);
    $("#repost-original").html('');
    $("#repost-text").val('');
});

// Отправка репоста
$(document).on('click', '#send-repost-btn', function () {
    const postId = $(this).data("post-id");
    const text = $("#repost-text").val();

    if (!postId) {
        console.error("Не удалось получить ID поста");
        return;
    }

    $.ajax({
        url: `/posts/repost/${postId}/`,
        type: 'POST',
        data: {
            'text': text,
            'csrfmiddlewaretoken': getCookie('csrftoken')
        },
        success: function (data) {
            $("#repostModal").fadeOut(150);
            $("#repost-text").val("");

            let counter = $('#repost-count-' + postId);
            let modalcounter = $('#modal-repost-count-' + postId);
            counter.text( parseInt(counter.text()) + 1 );
            modalcounter.text( parseInt(modalcounter.text()) + 1 );
        },
        error: function (err) {
            console.error(err);
            alert("Ошибка при отправке репоста");
        }
    });
});



// Получение cookie CSRF
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
