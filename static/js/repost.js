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

            let imagesHTML = '';
                data.orig_images.forEach(img => {
                    imagesHTML += `<img src="/media/${img.image}" class="r-img" style="max-width:200px;border-radius:10px;margin-top:10px;">`;
                });

                let newPost = `
                    <div class="post" data-post-id="${data.id}" id="post-item-${data.id}">
            
                        <div class="post open-post" data-post-id="${data.id}">
                            <p style="color:green;">
                                🔁 ${data.author} сделал репост
                            </p>
            
                            ${data.text ? `<p>${data.text}</p>` : ''}
            
                            <div class="repost-box" style="border:1px solid #ccc;padding:10px;border-radius:10px;">
                            <p>
                                <img src="/media/avatars/${data.avatar}" class="round" style="width:40px;height:40px;">
                            </p>
                                <h3>${data.orig_author}</h3>
                                <p>${data.orig_content}</p>
                                ${imagesHTML}
                            </div>
                        </div>
            
                        <button class="like-btn" data-post-id="${data.id}">
                            <i class="fa-regular fa-heart"></i>
                        </button>
                        <span id="like-actual-${data.id}">0</span>
            
                        <i class="fa-regular fa-comment"></i>
                        <span id="comment-count">0</span>
            
                        <button class="repost-btn" data-post-id="${data.id}">
                            <i class="fa-solid fa-retweet"></i>
                        </button>
                        <span id="repost-count-${data.id}">0</span>
            
                        <button class="del-post-btn" data-post-id="${data.id}">
                            <i class="fa-regular fa-trash-can"></i>
                        </button>
                    </div>
                `;

            // Добавляем новый репост в начало
            $("#posts-container").prepend(newPost);
        }

    });

});



// Получение cookie CSRF
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
