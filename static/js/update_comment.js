document.addEventListener("click", function (e) {

    // ---------- НАЖАТИЕ "РедАКТИРОВАТЬ" ----------
    if (e.target.classList.contains("edit-comment-btn")) {
        e.preventDefault();

        const commentId = e.target.dataset.commentId;
        const li = document.getElementById(`modal-comment-${commentId}`);
        const textSpan = li.querySelector(".comment-text");

        // если уже редактируется — выходим
        if (li.querySelector("textarea")) return;

        const oldText = textSpan.textContent.trim();

        // textarea
        const textarea = document.createElement("textarea");
        textarea.value = oldText;
        textarea.rows = 2;
        textarea.classList.add("edit-comment-textarea");

        // кнопка сохранить
        const saveBtn = document.createElement("button");
        saveBtn.textContent = "Сохранить";
        saveBtn.classList.add("save-comment-btn");
        saveBtn.dataset.commentId = commentId;

        // кнопка отмена
        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "Отмена";
        cancelBtn.classList.add("cancel-comment-btn");

        textSpan.replaceWith(textarea);
        e.target.after(cancelBtn);
        e.target.after(saveBtn);
        e.target.style.display = "none";
    }

    // ---------- ОТМЕНА ----------
    if (e.target.classList.contains("cancel-comment-btn")) {
        const li = e.target.closest("li");
        const textarea = li.querySelector("textarea");
        const oldText = textarea.value;

        const span = document.createElement("span");
        span.classList.add("comment-text");
        span.textContent = oldText;

        textarea.replaceWith(span);

        li.querySelector(".edit-comment-btn").style.display = "inline";
        li.querySelector(".save-comment-btn").remove();
        e.target.remove();
    }

    // ---------- СОХРАНЕНИЕ ----------
    if (e.target.classList.contains("save-comment-btn")) {
        const commentId = e.target.dataset.commentId;
        const li = document.getElementById(`modal-comment-${commentId}`);
        const textarea = li.querySelector("textarea");
        const newText = textarea.value.trim();

        if (!newText) return;

        fetch(`/posts/update_comment/${commentId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `text=${encodeURIComponent(newText)}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                const span = document.createElement("span");
                span.classList.add("comment-text");
                span.textContent = data.text;

                textarea.replaceWith(span);

                li.querySelector(".edit-comment-btn").style.display = "inline";
                li.querySelector(".cancel-comment-btn").remove();
                e.target.remove();
            }
        });
    }
});

// ---------- CSRF ----------
function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}
