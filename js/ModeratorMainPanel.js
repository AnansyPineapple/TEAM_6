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
            
            grid.appendChild(row);
        });
    } catch (error) {
        console.error('Ошибка при загрузке задач:', error);
    }
}

// Обновляем список каждые 30 секунд
setInterval(loadTasks, 30000);