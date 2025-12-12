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

    fetch(`/posts/paginate/?page=1&sort=${sort}`)
        .then(res => res.json())
        .then(data => {
            document.querySelector("#posts-container").innerHTML = data.posts_html;

            nextPage = data.next_page || 2;
            hasNext = data.has_next;
        });
});