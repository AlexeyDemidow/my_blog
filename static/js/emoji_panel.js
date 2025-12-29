document.addEventListener('DOMContentLoaded', () => {
    const emojiBtn = document.getElementById('emoji-btn');
    const emojiPanel = document.getElementById('emoji-panel');
    const messageInput = document.getElementById('message-input');

    emojiBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // останавливаем всплытие, чтобы клик по кнопке не закрывал панель
        emojiPanel.style.display = emojiPanel.style.display === 'none' ? 'block' : 'none';
    });

    emojiPanel.querySelectorAll('.emoji').forEach(el => {
        el.addEventListener('click', () => {
            messageInput.value += el.textContent;
            messageInput.focus();
        });
    });

    document.addEventListener('click', (e) => {
        if (!emojiPanel.contains(e.target) && e.target !== emojiBtn) {
            emojiPanel.style.display = 'none';
        }
    });
});
