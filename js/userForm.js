document.querySelector(".form_container").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const description = document.getElementById("description").value;

    console.log("Получено описание:", description);

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
        localStorage.setItem('form_data', JSON.stringify(result));
        
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке запроса. Попробуйте еще раз.');
    }
});