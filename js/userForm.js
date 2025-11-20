
document.querySelector(".form_container").addEventListener("submit", function(e) {
    e.preventDefault(); // ❗ Останавливаем стандартную отправку (и перезагрузку)
    
    const description = document.getElementById("description").value;

    console.log("Получено описание:", description);

    // Здесь можешь делать что угодно:
    // отправлять fetch, показать alert, скрыть форму и т.д.
});
