document.addEventListener("click", function(e) {

    // Клик по посту → открыть модалку
    let block = e.target.closest(".open-post");
    if (block) {
        let postId = block.dataset.postId;

        fetch(`/posts/post_detail/${postId}/`)
            .then(res => res.text())
            .then(html => {
                document.getElementById("post-modal-body").innerHTML = html;
                document.getElementById("post-modal").style.display = "block";
                syncOnlineStatus();
            });
    }

    // закрытие окна
    if (e.target.classList.contains("post-modal-close")) {
        document.getElementById("post-modal").style.display = "none";
    }
});

document.addEventListener("change", function (e) {

    if (e.target.classList.contains("modal-sort-selector")) {

        let comms_sort = e.target.value;
        let postId = e.target.dataset.postId;

        fetch(`/posts/post_detail/${postId}/?comms_sort=${comms_sort}`)
            .then(res => res.text())
            .then(html => {
                // Берём только комментарии
                let parser = new DOMParser();
                let doc = parser.parseFromString(html, "text/html");
                let newComments = doc.querySelector(".comments");

                let oldComments = document.querySelector(`.comments[data-post-id="${postId}"]`);
                oldComments.innerHTML = newComments.innerHTML;
            });
    }
});
