
$(document).ready(function() {
    const csrf = getCookie('csrftoken');

    $('.like-btn').on('click', function(event) {
        event.preventDefault();
        const postId = $(this).data('post-id');
        let like = parseInt($('#like-actual-' + postId).html()) + 1
        // if (new_water < 0) {
        //     new_water = 0
        // }
        $.ajax({
            url: `/posts/like/${postId}/`,
            type: 'POST',
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken': csrf
            },
        success: function(data) {

            if (data.success === false) {
                console.log("Уже лайкнул");
                return;
            }

            $(this).text('Liked').attr('disabled', true);
            $('#like-actual-' + postId).html(like);

            }.bind(this),

            error: function(error) {
                console.error(error);
            }
        });
        });

    function getCookie(name) {
          const value = `; ${document.cookie}`;
          const parts = value.split(`; ${name}=`);
          if (parts.length === 2) {
            const csrfToken = parts.pop().split(';').shift();
            return csrfToken;
          }
          return null;
        }
});
