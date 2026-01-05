let loading = false;
let nextPage = 2;
let hasNext = true;

document.addEventListener("DOMContentLoaded", () => {
    const postsContainer = document.querySelector("#posts-container");
    if (!postsContainer) return; // Если контейнера нет, выходим

    const userId = postsContainer.dataset.userId || null; // null = Home page

    function getFetchUrl(page, sort) {
        if (userId) {
            return `/posts/paginate_profile/${userId}/?page=${page}&sort=${sort}`;
        } else {
            return `/posts/paginate_home/?page=${page}&sort=${sort}`;
        }
    }

    function loadMorePosts() {
        if (loading || !hasNext) return;
        loading = true;

        let sort = document.getElementById("sort-selector").value;

        fetch(getFetchUrl(nextPage, sort))
            .then(res => res.json())
            .then(data => {
                postsContainer.insertAdjacentHTML("beforeend", data.posts_html);

                hasNext = data.has_next;
                if (hasNext) nextPage = data.next_page;

                loading = false;

                if (typeof syncOnlineStatus === "function") {
                    syncOnlineStatus();
                }
            });
    }

    // Скролл
    window.addEventListener("scroll", () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            loadMorePosts();
        }
    });

    // Смена сортировки
    const sortSelector = document.getElementById("sort-selector");
    if (sortSelector) {
        sortSelector.addEventListener("change", () => {
            postsContainer.innerHTML = "";
            nextPage = 1;
            hasNext = true;
            loadMorePosts();
        });
    }
});
