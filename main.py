import logging
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__) #CORS ошибки
CORS(flask_app)

@flask_app.route('/generate_route', methods=['POST'])
def generate_route():
    try:
        data = request.json
        
        # Получаем описание из запроса
        description = data.get('query')
        
        logger.info("🚗 ПОЛУЧЕН ЗАПРОС НА ГЕНЕРАЦИЮ МАРШРУТА:")
        logger.info(f"   Описание: {description}")
        logger.info("=" * 50)
        
        # Здесь можно добавить логику генерации маршрута
        # Пока просто сохраним как опрос
        
        survey_data = {
            "timestamp": datetime.now().isoformat(),
            "question": "Генерация маршрута",
            "answer": description,
            "question_id": "route_generation"
        }
        
        # Сохраняем в оба файла
        with open('survey_responses.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] ГЕНЕРАЦИЯ МАРШРУТА\n")
            f.write(f"         Описание: {description}\n")
            f.write("-" * 40 + "\n")
        
        with open('survey_data.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(survey_data, ensure_ascii=False) + '\n')
        
        # Возвращаем ответ для клиента
        return jsonify({
            "status": "success", 
            "message": "Route request received",
            "received_description": description,
            "route_data": {
                "points": ["Точка A", "Точка B"],
                "distance": "5 km",
                "duration": "1 hour"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки маршрута: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    flask_app.run(debug=True)