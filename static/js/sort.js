$(document).on('change', '#sort-selector', function() {
    let sort = $(this).val();

    $.ajax({
        url: window.location.pathname,
        type: 'GET',
        data: { sort: sort },

        success: function(response) {
            let newPosts = $(response).find('#posts-container').html();
            $('#posts-container').html(newPosts);
        }
    });
});