import json
import traceback
import sys
import datetime
from pathlib import Path

# * Глобальний журнал сеансу
session_log = {
    "початок_сесії": str(datetime.datetime.now()),
    "події": [],
    "помилка": None
}

#  * Згенерувати унікальне ім'я файлу на основі позначки часу в папці logs
def get_unique_filename(base_name, ext="html", folder="logs"):
    Path(folder).mkdir(parents=True, exist_ok=True)  # створює папку, якщо її немає
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(Path(folder) / f"{base_name}_{timestamp}.{ext}")

#  * Декоратор для логування функцій
def log_function(func):
    def wrapper(*args, **kwargs):
        event = {
            "крок": len(session_log["події"]) + 1,
            "функція": func.__name__,
            "аргументи": args,
            "ключові_аргументи": kwargs,
            "час": str(datetime.datetime.now()),
            "статус": "початок",
            "результат": None
        }
        session_log["події"].append(event)
        try:
            result = func(*args, **kwargs)
            event["статус"] = "успіх"
            event["результат"] = result
            return result
        except Exception as e:
            event["статус"] = "помилка"
            log_exception(e, event)
            raise
    return wrapper

# * Функція для логування винятків
def log_exception(e: Exception, event_info=None):
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    session_log["помилка"] = {
        "тип": str(type(e).__name__),
        "повідомлення": str(e),
        "traceback": tb_str,
        "у_якій_функції": event_info["функція"] if event_info else None,
        "крок": event_info["крок"] if event_info else None,
        "час": str(datetime.datetime.now())
    }
    
    # * Зберегти звіт JSON
    json_filename = get_unique_filename("звіт_помилки", "json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(session_log, f, indent=4, ensure_ascii=False)
    
    # * Згенерувати HTML-звіт
    html_filename = get_unique_filename("звіт_помилки", "html")
    generate_html_report(session_log, html_filename)

    # * Функція для генерації HTML з даних JSON
def generate_html_report(data, html_filename):
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Звіт Python</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            .event, .error {{ border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
            .успіх {{ background-color: #e0f7e0; }}
            .помилка {{ background-color: #f8d7da; }}
            pre {{ background-color: #f4f4f4; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Звіт сесії Python</h1>
        <p><strong>Початок сесії:</strong> {data['початок_сесії']}</p>
        <h2>Події</h2>
    """
    for event in data["події"]:
        status_class = "успіх" if event["статус"] == "успіх" else "помилка" if event["статус"] == "помилка" else ""
        html_content += f"""
        <div class="event {status_class}">
            <p><strong>Крок:</strong> {event['крок']}</p>
            <p><strong>Функція:</strong> {event['функція']}</p>
            <p><strong>Аргументи:</strong> {event['аргументи']}</p>
            <p><strong>Ключові аргументи:</strong> {event['ключові_аргументи']}</p>
            <p><strong>Час:</strong> {event['час']}</p>
            <p><strong>Статус:</strong> {event['статус']}</p>
            <p><strong>Результат:</strong> {event['результат']}</p>
        </div>
        """
    if data["помилка"]:
        html_content += f"""
        <h2>Помилка</h2>
        <div class="error">
            <p><strong>Тип:</strong> {data['помилка']['тип']}</p>
            <p><strong>Повідомлення:</strong> {data['помилка']['повідомлення']}</p>
            <p><strong>У функції:</strong> {data['помилка']['у_якій_функції']}</p>
            <p><strong>Крок:</strong> {data['помилка']['крок']}</p>
            <p><strong>Час:</strong> {data['помилка']['час']}</p>
            <pre>{data['помилка']['traceback']}</pre>
        </div>
        """
    html_content += "</body></html>"
    
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)



# ? =============================== Ввід функцій ====================================================

# ! Вставити сюди функції для логування

@log_function
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    raise ValueError(f"Елемент {target} не знайдено")

# * Використання
try:
    numbers = [1, 3, 5, 7, 9, 11]
    # * Успішний пошук
    binary_search(numbers, 7)
    # ! Пошук з помилкою
    binary_search(numbers, 4)

except Exception:
    print("Сталася помилка, звіт JSON та HTML збережено з унікальними іменами файлів")

