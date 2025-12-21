let loading = false;
let nextPage = 2;  // начинаем со 2 страницы
let hasNext = true;

function loadMorePosts() {
    if (loading || !hasNext) return;
    loading = true;

    let sort = document.getElementById("sort-selector").value;

    fetch(`/posts/paginate/?page=${nextPage}&sort=${sort}`)
        .then(res => res.json())
        .then(data => {
            console.log(data)
            document.querySelector("#posts-container").insertAdjacentHTML("beforeend", data.posts_html);

            hasNext = data.has_next;
            if (hasNext) nextPage = data.next_page;

            loading = false;
            syncOnlineStatus();
        });
}

window.addEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        loadMorePosts();
    }
});
