document.addEventListener('click', function (e) {
    const btn = e.target.closest('.pin-message-btn');
    if (!btn) return;

    e.stopPropagation();

    fetch(btn.dataset.pinUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': window.CSRF_TOKEN
        }
    })
    .then(r => r.json())
    .then(data => {
        const message = btn.closest('.message');

        if (data.is_pinned) {
            message.classList.add('pinned');
            document.getElementById('pinned-messages').prepend(message);
            btn.textContent = 'Открепить';
        } else {
            message.classList.remove('pinned');
            document.getElementById('normal-messages').append(message);
            btn.textContent = 'Закрепить';
        }
    });
});
