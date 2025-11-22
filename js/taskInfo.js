// taskInfo.js - ТОЛЬКО ОТОБРАЖЕНИЕ ДАННЫХ
document.addEventListener('DOMContentLoaded', function() {
    const taskId = localStorage.getItem('currentTaskId');
    
    if (taskId) {
        loadTaskData(taskId);
        updateTimer();
    } else {
        alert('Ошибка: ID задачи не найден');
        goBack();
    }
});

async function loadTaskData(taskId) {
    try {
        console.log('Загрузка данных для задачи ID:', taskId);
        
        // Прямой запрос к конкретной задаче
        const response = await fetch(`https://team-6-render.onrender.com/tasks/${taskId}`);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        
        const task = await response.json();
        console.log('Получены данные задачи:', task);
        
        if (task && task.complaint_id) {
            displayTaskData(task);
        } else {
            alert('Заявка не найдена');
            goBack();
        }
    } catch (error) {
        console.error('Ошибка при загрузке данных задачи:', error);
        // Пробуем альтернативный способ через список всех задач
        try {
            const response = await fetch(`https://team-6-render.onrender.com/tasks/${taskId}`);
            const task = await response.json();
            
            if (!task || task.error) {
                alert('Заявка не найдена');
                goBack();
                return;
            }
            
displayTaskData(task);
        } catch (secondError) {
            console.error('Ошибка при альтернативной загрузке:', secondError);
            alert('Ошибка при загрузке данных задачи');
        }
    }
}

function displayTaskData(task) {
    // Отображаем данные в карточке
    document.getElementById('task-id').textContent = task.complaint_id;
    document.getElementById('complaint_id_display').textContent = task.complaint_id;
    document.getElementById('status_display').textContent = getStatusText(task.status);
    document.getElementById('description_display').textContent = task.description || 'Описание отсутствует';
    
    // Форматируем даты
    const createdDate = new Date(task.created_at);
    document.getElementById('creation_date_display').textContent = formatDateForDisplay(createdDate);
    
    // Расчет сроков
    const deadline = calculateDeadline(createdDate);
    document.getElementById('deadline_system_display').textContent = formatDateForDisplay(deadline);
    document.getElementById('execution-date').textContent = formatDateForDisplay(deadline);
    document.getElementById('deadline-date').textContent = formatDateForDisplay(deadline);
    
    // Дополнительные поля
    document.getElementById('district_display').textContent = task.district || 'Не указан';
    document.getElementById('executor_display').textContent = task.executor_id ? `Исполнитель #${task.executor_id}` : 'Не назначен';
    
    // Обновляем таймер
    updateTimeRemaining(deadline);
}

function getStatusText(status) {
    const statusMap = {
        'moderated': 'На модерации',
        'in_progress': 'В работе',
        'completed': 'Завершено',
        'rejected': 'Отклонено'
    };
    return statusMap[status] || status;
}

function formatDateForDisplay(date) {
    return date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function calculateDeadline(createdDate) {
    // Используем deadline из базы или рассчитываем по умолчанию +7 дней
    const deadline = new Date(createdDate);
    deadline.setDate(deadline.getDate() + 7);
    return deadline;
}

function updateTimeRemaining(deadline) {
    const now = new Date();
    const timeDiff = deadline - now;
    
    const timeRemainingElement = document.getElementById('time-remaining');
    const standardTimeElement = document.getElementById('standard-time-remaining');
    
    if (timeDiff > 0) {
        const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
        
        const timeText = `${days} д. ${hours} ч. ${minutes} мин.`;
        timeRemainingElement.textContent = timeText;
        standardTimeElement.textContent = timeText;
    } else {
        timeRemainingElement.textContent = 'Срок истек';
        standardTimeElement.textContent = 'Срок истек';
        timeRemainingElement.style.color = 'red';
        standardTimeElement.style.color = 'red';
    }
}

function updateTimer() {
    setInterval(() => {
        const now = new Date();
        document.getElementById('current-time').textContent = 
            now.toLocaleTimeString('ru-RU');
    }, 1000);
}

function goBack() {
    window.location.href = 'ModeratorMainPanel.html';
}    