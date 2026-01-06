document.addEventListener("click", function (e) {

    // ---------- ОТКРЫТЬ РЕДАКТИРОВАНИЕ ----------
    if (e.target.classList.contains("edit-message-btn")) {
        e.preventDefault();

        const messageId = e.target.dataset.messageId;
        const messageDiv = document.querySelector(`.message[data-id="${messageId}"]`);
        const textDiv = messageDiv.querySelector(".text");

        // если уже редактируем
        if (textDiv.querySelector("textarea")) return;

        const oldText = textDiv.childNodes[0].textContent.trim();

        const textarea = document.createElement("textarea");
        textarea.value = oldText;
        textarea.rows = 2;
        textarea.classList.add("edit-message-textarea");

        // ⌨️ Enter / Shift+Enter / Esc
        textarea.addEventListener("keydown", function (e) {
            // Enter — сохранить
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                saveEditedMessage(messageId);
            }

            // Esc — отмена
            if (e.key === "Escape") {
                cancelEdit(messageDiv, oldText);
            }
        });

        const saveBtn = document.createElement("button");
        saveBtn.textContent = "Сохранить";
        saveBtn.classList.add("save-message-btn");
        saveBtn.dataset.messageId = messageId;

        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "Отмена";
        cancelBtn.classList.add("cancel-message-btn");

        textDiv.innerHTML = "";
        textDiv.appendChild(textarea);
        textDiv.appendChild(saveBtn);
        textDiv.appendChild(cancelBtn);
    }

    // ---------- ОТМЕНА ----------
    if (e.target.classList.contains("cancel-message-btn")) {
        const messageDiv = e.target.closest(".message");
        const textarea = messageDiv.querySelector("textarea");
        const oldText = textarea.value;

        const textDiv = messageDiv.querySelector(".text");
        textDiv.innerHTML = `
            ${oldText}
            <span class="chat-time"></span>
        `;
    }

    // ---------- СОХРАНИТЬ ----------
    if (e.target.classList.contains("save-message-btn")) {
        const messageId = e.target.dataset.messageId;
        const messageDiv = document.querySelector(`.message[data-id="${messageId}"]`);
        const textarea = messageDiv.querySelector("textarea");
        const newText = textarea.value.trim();

        if (!newText) return;

        fetch(`/chat/update_message/${messageId}/`, {
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
                const textDiv = messageDiv.querySelector(".text");
                textDiv.innerHTML = `
                    ${data.text}
                    <span class="chat-time">отредактировано</span>
                `;
            }
        });
        textarea.addEventListener("input", () => {
            textarea.style.height = "auto";
            textarea.style.height = textarea.scrollHeight + "px";
        });

    }
});

function saveEditedMessage(messageId) {
    const messageDiv = document.querySelector(`.message[data-id="${messageId}"]`);
    const textarea = messageDiv.querySelector("textarea");
    const newText = textarea.value.trim();

    if (!newText) return;

    fetch(`/chat/update_message/${messageId}/`, {
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
            const textDiv = messageDiv.querySelector(".text");
            textDiv.innerHTML = `
                ${data.text}
                <span class="chat-time">отредактировано</span>
            `;
        }
    });
}

function cancelEdit(messageDiv, oldText) {
    const textDiv = messageDiv.querySelector(".text");
    textDiv.innerHTML = `
        ${oldText}
        <span class="chat-time"></span>
    `;
}



// ---------- CSRF ----------
function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}
