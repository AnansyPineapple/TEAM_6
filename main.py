import logging
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__) #CORS ошибки
CORS(flask_app)

@flask_app.route('/save_survey', methods=['POST'])
def save_survey():
    try:
        data = request.json
        
        user_text = data.get('user_text')
        question_id = data.get('question_id') 
        question_text = data.get('question_text')
        timestamp = data.get('timestamp')
        
        logger.info("📝 ПОЛУЧЕН ОТВЕТ ОПРОСА:")
        logger.info(f"   Вопрос: {question_text}")
        logger.info(f"   Ответ: {user_text}")
        logger.info(f"   ID вопроса: {question_id}")
        logger.info(f"   Время: {timestamp}")
        logger.info("=" * 50)
        
        # Сохраняем в файл
        with open('survey_responses.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] Q: {question_text}\n")
            f.write(f"         A: {user_text}\n")
            f.write(f"         ID: {question_id}\n")
            f.write("-" * 40 + "\n")
        
        # JSON файл
        survey_data = {
            "timestamp": datetime.now().isoformat(),
            "question": question_text,
            "answer": user_text,
            "question_id": question_id
        }
        
        with open('survey_data.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(survey_data, ensure_ascii=False) + '\n')
        
        return jsonify({
            "status": "success", 
            "message": "Survey response saved"
        })
        
    except Exception as e:
        logger.info(f"❌ Ошибка сохранения опроса: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    flask_app.run(debug=True)