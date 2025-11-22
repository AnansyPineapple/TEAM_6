// taskInfo.js - ОТОБРАЖЕНИЕ ДАННЫХ ПО ЗАЯВКЕ

document.addEventListener('DOMContentLoaded', () => {
    const taskId = localStorage.getItem('currentTaskId');

    if (!taskId) {
        alert('Ошибка: ID задачи не найден');
        goBack();
        return;
    }

    loadTaskData(taskId);
});


// ===============================
// 📌 ЗАГРУЗКА ДАННЫХ
// ===============================

async function loadTaskData(taskId) {
    try {
        console.log(`Загружаем данные заявки ID: ${taskId}`);

        const response = await fetch(`https://team-6-render.onrender.com/tasks/${taskId}`);

        if (!response.ok) {
            throw new Error(`HTTP ошибка ${response.status}`);
        }

        const task = await response.json();
        console.log('Ответ сервера:', task);

        if (!task || task.error) {
            alert('Заявка не найдена');
            goBack();
            return;
        }

        displayTaskData(task);

    } catch (err) {
        console.error("Ошибка загрузки:", err);
        alert('Не удалось загрузить данные заявки');
        goBack();
    }
}


// ===============================
// 📌 ОТОБРАЖЕНИЕ ДАННЫХ
// ===============================

function displayTaskData(task) {
    // --- Простые текстовые поля ---
    safeSet('task-id', task.complaint_id);
    safeSet('complaint_id_display', task.complaint_id);
    safeSet('description_display', task.description || 'Описание отсутствует');
    safeSet('district_display', task.district || 'Не указан');
    safeSet('executor_display', task.executor_id ? `Исполнитель #${task.executor_id}` : 'Не назначен');
    safeSet('status_display', getStatusText(task.status));

    // --- Дата создания ---
    const created = parseDate(task.created_at);
    safeSet('creation_date_display', formatDate(created));

    // --- Дедлайны ---
    const computedDeadline = computeDeadline(task);
    safeSet('deadline_system_display', formatDate(computedDeadline));
    safeSet('execution-date', formatDate(computedDeadline));
    safeSet('deadline-date', formatDate(computedDeadline));

    // --- Таймеры ---
    updateTimeRemaining(computedDeadline);
}


// ===============================
// 📌 ПОДДЕРЖИВАЮЩИЕ ФУНКЦИИ
// ===============================

// безопасно устанавливает текстовое содержимое
function safeSet(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? '—';
}

function getStatusText(status) {
    const map = {
        moderated: 'На модерации',
        in_progress: 'В работе',
    completed: 'Завершено',
        rejected: 'Отклонено'
    };
    return map[status] || status || 'Не указан';
}

// Парсинг даты
function parseDate(value) {
    const d = new Date(value);
    return isNaN(d.getTime()) ? null : d;
}

// форматирование даты
function formatDate(d) {
    if (!d) return '—';
    return d.toLocaleDateString('ru-RU') + ' ' + d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

// Вычисление дедлайна: если есть deadline в базе — берем его.
// если нет — создаем +7 дней
function computeDeadline(task) {
    if (task.deadline) {
        const d = parseDate(task.deadline);
        if (d) return d;
    }

    const created = parseDate(task.created_at) ?? new Date();
    const deadline = new Date(created);
    deadline.setDate(deadline.getDate() + 7);

    return deadline;
}

// Кнопка назад
function goBack() {
    window.location.href = "ModeratorMainPanel.html";
}
