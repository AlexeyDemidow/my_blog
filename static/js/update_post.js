document.addEventListener("DOMContentLoaded", () => {
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const newForms = document.querySelectorAll(".image-form");


    // ---------- Добавление нового поля ----------
    document.getElementById("add-photo").addEventListener("click", () => {
        for (let form of newForms) {
            if (form.style.display === "none") {
                form.style.display = "block"; // показываем скрытую форму
                return; // только одно поле за клик
            }
        }
        alert("Все поля уже добавлены");
    });

    // ---------- Превью и удаление новых изображений ----------
    newForms.forEach(form => {
        const input = form.querySelector("input[type='file']");
        const preview = form.querySelector(".preview-new");
        const removeBtn = form.querySelector(".remove-image");

        input.addEventListener("change", () => {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = e => {
                    preview.src = e.target.result;
                    preview.style.display = "block";
                    removeBtn.style.display = "inline-block";
                };
                reader.readAsDataURL(input.files[0]);
            }
        });

        removeBtn.addEventListener("click", () => {
            input.value = "";
            preview.style.display = "none";
            removeBtn.style.display = "none";
            form.style.display = "none"; // скрываем форму обратно
        });
    });
});
