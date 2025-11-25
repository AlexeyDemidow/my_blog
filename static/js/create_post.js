document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".image-form");

    if (forms.length > 0) {
        forms[0].style.display = "block";
    }

    forms.forEach((form, index) => {
        const input = form.querySelector("input[type='file']");
        const preview = form.querySelector(".preview");
        const removeBtn = form.querySelector(".remove-image");

        if (!input || !preview || !removeBtn) return;

        const updatePreview = () => {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.style.display = "block";
                    removeBtn.style.display = "inline-block";
                };
                reader.readAsDataURL(input.files[0]);
            } else {
                preview.src = "";
                preview.style.display = "none";
                removeBtn.style.display = "none";
            }
        };

        input.addEventListener("change", () => {
            updatePreview();

            // Показать следующее поле, если текущее заполнено
            const nextForm = forms[index + 1];
            if (input.files.length > 0 && nextForm) {
                nextForm.style.display = "block";
            }
        });

        removeBtn.addEventListener("click", () => {
            // очищаем поле и скрываем превью
            input.value = "";
            updatePreview();

            // скрываем полностью контейнер поля
            form.style.display = "none";

        });

        // Инициализация при загрузке страницы
        updatePreview();
    });

});
