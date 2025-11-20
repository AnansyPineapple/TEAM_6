import logging
import json

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__) #CORS ошибки
CORS(flask_app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@flask_app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        if not data:
            print("❌ Нет JSON данных в запросе")
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Получаем описание из запроса
        description = data.get('query')
        
        logger.info("🚗 ПОЛУЧЕН ЗАПРОС НА ГЕНЕРАЦИЮ МАРШРУТА:")
        logger.info(f"   Описание: {description}")
        logger.info("=" * 50)
        
        # Пока просто сохраним как опрос
        result = {
            "answer": description,
        }

        response = jsonify(result)
        return response
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)