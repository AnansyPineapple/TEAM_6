# main.py (дополненный)
import logging
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
CORS(flask_app)

class QueryDatabase:
    def __init__(self, db_name='querys.db'):
        self.db_name = db_name
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT NOT NULL DEFAULT 'moderated',
                created_at DATETIME NOT NULL,
                description TEXT NOT NULL,
                district INTEGER,
                resolution TEXT,
                execution_date DATE,
                executor_id INTEGER,
                final_status_at DATE,
                deadline DATE
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_task(self, description):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO tasks (created_at, description)
            VALUES (?, ?)
        ''', (current_time, description))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Новая задача добавлена с описанием: {description}")
    
    def get_all_tasks(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def update_task_status(self, complaint_id, status):
        """Обновляет статус задачи"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, final_status_at = ?
            WHERE complaint_id = ?
        ''', (status, datetime.now().isoformat(), complaint_id))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Статус задачи {complaint_id} изменен на: {status}")

query_db = QueryDatabase()

@flask_app.route('/send', methods=['POST', 'OPTIONS'])
def send():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        description = data.get('query')
        
        if not description:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        # Сохраняем задачу в базу данных
        query_db.add_task(description)
        
        response_data = {
            "status": "success",
            "message": "Заявка успешно создана",
            "received_query": description,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке запроса: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@flask_app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = query_db.get_all_tasks()
        return jsonify(tasks), 200
    except Exception as e:
        logger.error(f"❌ Ошибка при получении задач: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000, debug=True)