import logging
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from GPT import analyze_single_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
CORS(flask_app, resources={r"/*": {"origins": "*"}})


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
                execution_date TEXT,
                executor_id INTEGER,
                final_status_at DATE,
                deadline TEXT
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


query_db = QueryDatabase()


def build_task_for_ai(task_id, executor_reply):
    conn = sqlite3.connect('querys.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE complaint_id = ?', (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    task = dict(row)
    task["executor_reply"] = executor_reply
    return task


@flask_app.route('/send-to-ai', methods=['POST', 'OPTIONS'])
def send_to_ai():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.json
    task_id = data.get("task_id")
    executor_reply = data.get("executor_reply", "")

    task_full = build_task_for_ai(task_id, executor_reply)
    if not task_full:
        return jsonify({"error": "Task not found"}), 404

    # 🔹 Используем GPT.py для анализа
    ai_result = analyze_single_response(executor_reply)

    # Обновление БД
    conn = sqlite3.connect('querys.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks SET 
            status = ?,
            resolution = ?,
            execution_date = ?
        WHERE complaint_id = ?
    """, (
        "closed" if ai_result.get("is_promise") else "moderated",
        ai_result.get("response_text"),
        ai_result.get("deadline", None),
        task_id
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok",
        "ai_result": ai_result
    })


@flask_app.route('/send', methods=['POST', 'OPTIONS'])
def send():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    description = data.get('query')
    if not description:
        return jsonify({"error": "Missing 'query' field"}), 400
    query_db.add_task(description)
    return jsonify({
        "status": "success",
        "message": "Заявка успешно создана",
        "received_query": description,
        "timestamp": datetime.now().isoformat()
    }), 200


@flask_app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = query_db.get_all_tasks()
        return jsonify(tasks), 200
    except Exception as e:
        logger.error(f"❌ Ошибка при получении задач: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@flask_app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        conn = sqlite3.connect('querys.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE complaint_id = ?', (task_id,))
        task = cursor.fetchone()
        conn.close()
        if task:
            return jsonify(dict(task)), 200
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        logger.error(f"❌ Ошибка при получении задачи: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# 🔹 Очередь дедлайнов
def notify_upcoming_deadlines():
    while True:
        try:
            conn = sqlite3.connect('querys.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            today = datetime.now()
            check_date = today + timedelta(days=4)
            cursor.execute("SELECT * FROM tasks WHERE execution_date IS NOT NULL")
            tasks = cursor.fetchall()
            for task in tasks:
                try:
                    deadline_str = task['execution_date']
                    if deadline_str in ["НЕ_УСТАНОВЛЕН", "БОЛЕЕ_ГОДА", None]:
                        continue
                    deadline = datetime.strptime(deadline_str, "%d.%m.%y")
                    days_left = (deadline - today).days
                    if 0 <= days_left <= 4:
                        print(f"⚠️ Задача {task['complaint_id']} — осталось {days_left} дней до дедлайна")
                except:
                    continue
            conn.close()
            # Проверяем каждый час
            import time
            time.sleep(3600)
        except Exception as e:
            print("Ошибка в уведомлении дедлайнов:", e)
            time.sleep(60)


if __name__ == "__main__":
    threading.Thread(target=notify_upcoming_deadlines, daemon=True).start()
    flask_app.run(host="0.0.0.0", port=10000, debug=True)
