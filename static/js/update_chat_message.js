function initEditMessages(socket) {

    document.addEventListener("click", function (e) {

        const btn = e.target.closest(".edit-message-btn");
        if (!btn) return;

        e.preventDefault();

        const messageId = btn.dataset.messageId;
        const messageDiv = document.querySelector(`.message[data-id="${messageId}"]`);
        const textDiv = messageDiv.querySelector(".text");

        if (textDiv.querySelector("textarea")) return;

        const oldText = textDiv.querySelector(".message-text")?.textContent || textDiv.childNodes[0].textContent.trim();

        const textarea = document.createElement("textarea");
        textarea.className = "edit-message-textarea";
        textarea.value = oldText;
        textarea.rows = 2;

        textarea.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                saveEditedMessage(socket, messageId);
            }
            if (e.key === "Escape") {
                cancelEdit(messageDiv, oldText);
            }
        });

        textDiv.innerHTML = "";
        textDiv.appendChild(textarea);
        textarea.focus();
    });
}

function saveEditedMessage(socket, messageId) {
    const messageDiv = document.querySelector(`.message[data-id="${messageId}"]`);
    const textarea = messageDiv.querySelector("textarea");
    const newText = textarea.value.trim();

    if (!newText) return;

    socket.send(JSON.stringify({
        type: "edit_message",
        message_id: messageId,
        text: newText
    }));
}

document.addEventListener('click', function (e) {
    const btn = e.target.closest('.options-btn');

    document.querySelectorAll('.message-options-menu')
        .forEach(menu => menu.classList.remove('active'));

    if (btn) {
        e.stopPropagation();
        btn.parentElement.classList.add('active');
    }
});