$(document).on('click', '.sendPost-btn', function () {
    const postId = $(this).data('post-id');

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
                    html += `<img src="/media/${img.image}" alt="">`;
                });
            }

            $.get('/posts/dialogs_list/', function (res) {
            const select = $("#sendPost-dialog");
            select.empty().append('<option value="">Выберите диалог</option>');

            res.dialogs.forEach(d => {
                select.append(
                    `<option value="${d.id}">${d.title}</option>`
                );
            });
        });
            $("#sendPost-confirm-btn").data("post-id", postId);
            $("#sendPost-original").html(html);
            $("#sendPostModal").fadeIn(150);
        }
    });
});

$(document).on('click', '#sendPost-confirm-btn', function () {
    const postId = $(this).data('post-id');
    const dialogId = $("#sendPost-dialog").val();
    const text = $("#sendPost-text").val();

    if (!dialogId) {
        alert('Выберите диалог');
        return;
    }

    $.ajax({
        url: `/chat/send_post/${postId}/${dialogId}/`,
        type: 'POST',
        data: {
            text: text,
            csrfmiddlewaretoken: getCookie('csrftoken')
        },
        success: function () {
            $("#sendPostModal").fadeOut(150);
            $("#sendPost-text").val('');
            $("#sendPost-dialog").val('');
        }
    });
});

$(document).on('click', '.sendPost-close', function() {
    $("#sendPostModal").fadeOut(150);
    $("#sendPost-original").html('');
    $("#sendPost-text").val('');
});

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}