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
            });
    }

    // закрытие окна
    if (e.target.classList.contains("post-modal-close")) {
        document.getElementById("post-modal").style.display = "none";
    }
});
