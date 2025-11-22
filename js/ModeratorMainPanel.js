// ModeratorMainPanel.js
document.addEventListener('DOMContentLoaded', function() {
    loadTasks();
});

async function loadTasks() {
    try {
        const response = await fetch('https://team-6-render.onrender.com/tasks');
        const tasks = await response.json();
        
        const grid = document.querySelector('.grid');
        const existingRows = document.querySelectorAll('.grid_row');
        existingRows.forEach(row => row.remove());

        tasks.forEach(task => {
            const row = document.createElement('div');
            row.className = 'grid_row';
            row.setAttribute('data-task-id', task.complaint_id);
            
            row.innerHTML = `
                <div class="grid-cell">—</div>
                <div class="grid-cell">${task.complaint_id}</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">${task.description}</div>
                <div class="grid-cell">${task.status}</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">—</div>
                <div class="grid-cell">${new Date(task.created_at).toLocaleDateString()}</div>
                <div class="grid-cell">—</div>
            `;
            
            // Добавляем обработчик клика
            row.addEventListener('click', function() {
                openTaskInfo(task.complaint_id);
            });
            
            grid.appendChild(row);
        });
    } catch (error) {
        console.error('Ошибка при загрузке задач:', error);
    }
}

function openTaskInfo(taskId) {
    // Сохраняем ID задачи в localStorage для использования на странице taskInfo.html
    localStorage.setItem('currentTaskId', taskId);
    // Переходим на страницу с информацией о задаче
    window.location.href = 'taskInfo.html';
}

document.getElementById("send-to-ai").addEventListener("click", async function() {
    const taskId = localStorage.getItem('currentTaskId');
    const reply = document.getElementById("executor_reply").value;

    const response = await fetch("https://team-6-render.onrender.com/send-to-ai", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            task_id: taskId,
            executor_reply: reply
        })
    });

    const result = await response.json();
    console.log("AI RESULT:", result);
    alert("Ответ отправлен в ИИ!");
});

// Обновляем список каждые 30 секунд
setInterval(loadTasks, 30000);