document.addEventListener('DOMContentLoaded', function () {

    $('#follow-btn').on('click', function () {
        const userId = $(this).data('user-id');

        fetch(`/users/${userId}/follow/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(res => res.json())
        .then(data => {
            this.textContent = data.is_following
                ? 'Отписаться'
                : 'Подписаться';

            $('#followers-count').text(data.followers_count + ' Подписок');
        });
    });
});
