// userForm.js (обновленный)
document.querySelector(".form_container").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const description = document.getElementById("description").value;

    const data = {
        query: description
    };

    try {
        const response = await fetch('https://team-6-render.onrender.com/send', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Успешный ответ:", result);
        alert('Заявка успешно отправлена!');
        document.getElementById("description").value = ''; // Очищаем поле
        
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке запроса. Попробуйте еще раз.');
    }
});