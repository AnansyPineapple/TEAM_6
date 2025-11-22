import logging
import json
import sqlite3
from datetime import datetime

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

# Настраиваем логирование чтобы видеть все в консоли
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
CORS(flask_app)

# ЗАГЛУШКА - JSON массив заявок как в базе
APPLICATIONS_JSON = [
    {
        "complaint_id": 2,
        "status": "moderated",
        "created_at": "2024-01-16", 
        "description": "Сломан лифт в доме 25",
        "district": 3,
        "resolution": None,
        "execution_date": None,
        "executor_id": None,
        "final_status_at": None,
        "deadline": None
    }
]

class QueryDatabase:
    def __init__(self, db_name='querys.db'):
        self.db_name = db_name
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных и таблицы"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                complaint_id INTEGER PRIMARY KEY,
                status TEXT NOT NULL,
                created_at DATE NOT NULL,
                description TEXT NOT NULL,
                district INTEGER NOT NULL,
                resolution TEXT,
                execution_date DATE,
                executor_id INTEGER,
                final_status_at DATE,
                deadline DATE
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tasks_status_deadline 
            ON tasks(status, deadline) WHERE status = 'closed_with_promise'
        ''')
        
        # ЗАГРУЗКА ДАННЫХ ИЗ JSON В БАЗУ
        for app in APPLICATIONS_JSON:
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (complaint_id, status, created_at, description, district, resolution, execution_date, executor_id, final_status_at, deadline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                app['complaint_id'], app['status'], app['created_at'], app['description'], 
                app['district'], app['resolution'], app['execution_date'], app['executor_id'],
                app['final_status_at'], app['deadline']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ База данных {self.db_name} инициализирована с тестовыми данными")
    
    def get_closed_with_promise_tasks(self):
        """Получает все closed_with_promise задачи отсортированные по дедлайну"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = 'closed_with_promise'
            ORDER BY deadline ASC, created_at ASC
        ''')
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def mark_as_completed(self, complaint_id, resolution=None, executor_id=None):
        """Помечает задачу как выполненную"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = 'completed', 
                resolution = ?,
                executor_id = ?,
                execution_date = ?,
                final_status_at = ?
            WHERE complaint_id = ?
        ''', (
            resolution, 
            executor_id, 
            datetime.now().date().isoformat(),
            datetime.now().date().isoformat(),
            complaint_id
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Задача {complaint_id} помечена как выполненная")
    
    def get_task_stats(self):
        """Получает статистику по задачам"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                status,
                COUNT(*) as count,
                MAX(created_at) as last_created
            FROM tasks 
            GROUP BY status
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'count': row[1],
                'last_created': row[2]
            }
        
        conn.close()
        return stats
    
    def get_next_task(self):
        """Получает следующую задачу для обработки (самый ближайший дедлайн)"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = 'closed_with_promise'
            ORDER BY deadline ASC
            LIMIT 1
        ''')
        
        task = cursor.fetchone()
        conn.close()
        
        if task:
            return dict(task)
        return None

    def get_all_tasks(self):
        """Получает все задачи"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks ORDER BY deadline ASC')
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

# Инициализируем базу данных
query_db = QueryDatabase()

@flask_app.route('/send', methods=['POST', 'OPTIONS'])
def send():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            logger.error("❌ Получен пустой запрос или не JSON данные")
            return jsonify({"error": "No JSON data received"}), 400
        
        description = data.get('query')
        
        if not description:
            logger.error("❌ Отсутствует поле 'query' в данных")
            return jsonify({"error": "Missing 'query' field"}), 400
        
        logger.info(f"✅ Получено описание: {description}")
        
        response_data = {
            "status": "success",
            "message": "Данные успешно получены",
            "received_query": description,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке запроса: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000, debug=True)