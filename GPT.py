import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Настройки API YandexGPT
API_KEY = os.getenv("API_KEY")
FOLDER_ID = "b1g7mvadcsbaoiuvta8u"

# Промт для определения обещаний
PROMT_SYSTEM = """
Ты — эксперт по анализу ответов коммунальных служб. Определи, является ли ответ ОБЕЩАНИЕМ РЕШИТЬ ПРОБЛЕМУ в будущем.

КРИТЕРИИ ОБЕЩАНИЯ (должны быть ВСЕ условия):
1. Есть КОНКРЕТНОЕ указание на будущие действия по решению проблемы
2. Указаны СРОКИ или ПЛАНЫ выполнения
3. Ответ относится к РЕШЕНИЮ ПРОБЛЕМЫ, а не к процедурам или инструкциям

ПРИМЕРЫ ОБЕЩАНИЙ (отвечай "ДА"):
✓ "Работы будут выполнены до 30.09.2025г."
✓ "Замена окна запланирована на 2026 год"
✓ "Включено в план работ на 4 квартал"
✓ "Управляющими организациями проводятся работы по регулировке систем отопления. По практике, данный процесс занимает до 2 недель."

ПРИМЕРЫ НЕ-ОБЕЩАНИЙ (отвечай "НЕТ"):
✗ Инструкции: "Обратитесь в управляющую компанию"
✗ Процедуры: "Необходимо решение общего собрания"
✗ Констатации: "Проверка выполнена", "Мусор убран"
✗ Отказы без перспектив: "Не предусмотрено", "Невозможно"

Формат ответа: Только "ДА" или "НЕТ"
"""

# Промт для извлечения дат дедлайнов (исправленный - убраны фигурные скобки)
DEADLINE_EXTRACTION_PROMPT_TEMPLATE = """
Ты — специалист по извлечению дат дедлайнов из текстов коммунальных служб. Твоя задача — найти в ответе исполнителя указание на срок выполнения работ и преобразовать его в конкретную дату.

СЕГОДНЯШНЯЯ ДАТА: {today_date}

ИНСТРУКЦИЯ:
1. Внимательно проанализируй текст ответа исполнителя
2. Найди ВСЕ упоминания сроков, дат, периодов выполнения работ
3. Для относительных сроков ("в течение...", "в течении...") используй СЕГОДНЯШНЮЮ ДАТУ как точку отсчета
4. Преобразуй найденные сроки в формат ДД.ММ.ГГ

ПРАВИЛА ПРЕОБРАЗОВАНИЯ:
• Конкретные даты: "до 30.09.2025г." → 30.09.25
• Только год: "на 2026 год" → 31.12.26
• Кварталы: "4 квартал 2025" → 31.12.25
• Относительные сроки: "в течение 2 недель" → (сегодняшняя дата + 14 дней)
• "До конца месяца" → последний день текущего месяца
• "До конца года" → 31.12.ТЕКУЩИЙ_ГОД
• Месяц без числа: "в сентябре 2025" → 30.09.25
• Рабочие дни: "в течение 10 рабочих дней" → (сегодняшняя дата + 14 календарных дней)

ВАЖНО: Если срок выполнения превышает 1 год от сегодняшней даты, верни "БОЛЕЕ_ГОДА"

ЕСЛИ СРОКОВ НЕТ:
• Если в тексте нет конкретных указаний на сроки → "НЕ_УСТАНОВЛЕН"
• Если есть только общие фразы без дат → "НЕ_УСТАНОВЛЕН"
• Если указаны процедуры без сроков → "НЕ_УСТАНОВЛЕН"

Формат ответа: Только дата в формате ДД.ММ.ГГ или "НЕ_УСТАНОВЛЕН" или "БОЛЕЕ_ГОДА"
"""


def call_yandex_gpt(messages: list, max_retries: int = 3) -> tuple[str, str]:
    """Общая функция для вызова YandexGPT"""
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": "100"
        },
        "messages": messages
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {API_KEY}"
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
            response.raise_for_status()
            resp_json = response.json()

            # Извлекаем текст ответа
            answer_text = resp_json['result']['alternatives'][0]['message']['text'].strip()
            return answer_text, "success"

        except requests.exceptions.Timeout:
            error_msg = f"Таймаут запроса (попытка {attempt + 1}/{max_retries})"
            print(error_msg)
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка сети (попытка {attempt + 1}/{max_retries}): {e}"
            print(error_msg)
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
        except Exception as e:
            error_msg = f"Неожиданная ошибка (попытка {attempt + 1}/{max_retries}): {e}"
            print(error_msg)
            if attempt < max_retries - 1:
                time.sleep(5)
                continue

    return "", "Ошибка после всех попыток"


def is_promise(response_text: str) -> tuple[bool, str]:
    """Определяет, является ли ответ обещанием с помощью YandexGPT"""
    messages = [
        {
            "role": "system",
            "text": PROMT_SYSTEM
        },
        {
            "role": "user",
            "text": f"Ответ исполнителя: {response_text}"
        }
    ]

    answer_text, status = call_yandex_gpt(messages)

    if status != "success":
        return False, status

    # Упрощенная проверка ответа
    answer_upper = answer_text.upper()
    if "ДА" in answer_upper:
        return True, answer_text
    else:
        return False, answer_text


def extract_deadline(response_text: str) -> tuple[str, str]:
    """Извлекает дату дедлайна из ответа исполнителя"""
    # Получаем сегодняшнюю дату в формате ДД.ММ.ГГГГ для промта
    today = datetime.now()
    today_str = today.strftime("%d.%m.%Y")

    # Создаем промт с сегодняшней датой (заменяем ТЕКУЩИЙ_ГОД на реальный год)
    current_year = today.strftime("%y")
    current_prompt = DEADLINE_EXTRACTION_PROMPT_TEMPLATE.format(today_date=today_str)
    current_prompt = current_prompt.replace("ТЕКУЩИЙ_ГОД", current_year)

    messages = [
        {
            "role": "system",
            "text": current_prompt
        },
        {
            "role": "user",
            "text": f"Ответ исполнителя: {response_text}"
        }
    ]

    answer_text, status = call_yandex_gpt(messages)

    if status != "success":
        return "Ошибка извлечения", status

    return answer_text, "success"


def check_if_deadline_too_far(deadline_str: str) -> bool:
    """Проверяет, превышает ли дедлайн 1 год"""
    if deadline_str in ["НЕ_УСТАНОВЛЕН", "БОЛЕЕ_ГОДА", "Ошибка извлечения"]:
        return deadline_str == "БОЛЕЕ_ГОДА"

    try:
        # Парсим дату в формате ДД.ММ.ГГ
        deadline_date = datetime.strptime(deadline_str, "%d.%m.%y")
        today = datetime.now()

        # Проверяем разницу (больше 1 года = 365 дней)
        delta = deadline_date - today
        return delta.days > 365
    except ValueError:
        # Если не удалось распарсить дату
        return False


def analyze_single_response(response_text: str) -> Dict[str, Any]:
    """Анализирует один ответ инстанции и возвращает результат"""
    print(f"Анализ ответа исполнителя:")
    print(f"Текст: {response_text}")
    print("-" * 80)

    # Шаг 1: Определяем, является ли ответ обещанием
    is_promise_result, promise_answer = is_promise(response_text)

    result = {
        "response_text": response_text,
        "is_promise": is_promise_result,
        "promise_analysis_result": promise_answer,
        "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if is_promise_result:
        print("✓ ОБЕЩАНИЕ обнаружено")

        # Шаг 2: Извлекаем дедлайн
        deadline, deadline_status = extract_deadline(response_text)

        if deadline_status == "success":
            print(f"✓ Извлечен срок: {deadline}")

            # Шаг 3: Проверяем, не превышает ли дедлайн 1 год
            if check_if_deadline_too_far(deadline):
                print("✗ Срок превышает 1 год - обещание забыто")
                result["is_promise"] = False
                result["deadline"] = "БОЛЕЕ_ГОДА"
                result["forgotten_reason"] = "deadline_exceeds_one_year"
            else:
                result["deadline"] = deadline
                result["deadline_status"] = "valid"
        else:
            print(f"✗ Ошибка при извлечении срока: {deadline}")
            result["deadline"] = deadline
            result["deadline_status"] = "error"
    else:
        print("✗ НЕ является обещанием")

    print("=" * 80)
    return result


def main(test_response):
    """Пример использования для анализа одного ответа"""
    # Пример ответа инстанции (замените на реальный)

    # Анализируем ответ
    result = analyze_single_response(test_response)

    # Выводим результат
    print("\nРЕЗУЛЬТАТ АНАЛИЗА:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Сохраняем в файл
    with open("response_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nРезультат сохранен в файл 'response_analysis.json'")


if __name__ == "__main__":
    main()