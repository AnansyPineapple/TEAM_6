document.querySelector(".form_container").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const description = document.getElementById("description").value;

    console.log("Получено описание:", description);

    const data = {
        user_text: description,  // Изменяем поле на то, что ожидает сервер
        question_id: "form_question_1",  // Добавляем обязательные поля
        question_text: "Описание маршрута",
        timestamp: new Date().toISOString()
    };

    try {
        const response = await fetch('https://team-6-render.onrender.com/submit', {  // Изменяем URL
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

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Expected JSON, got:', text.substring(0, 200));
            throw new Error('Server returned non-JSON response');
        }

        const result = await response.json();
        localStorage.setItem('form_data', JSON.stringify(result));  // Исправляем ключ
        window.location.href = 'answer.html';
        
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке запроса. Попробуйте еще раз.');
    }
});