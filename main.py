import json
import traceback
import sys
import datetime
from pathlib import Path

# * Глобальний журнал сеансу
session_log = {
    "session_start": str(datetime.datetime.now()),
    "events": [],
    "error": None
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
            "step": len(session_log["events"]) + 1,
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "timestamp": str(datetime.datetime.now()),
            "status": "started",
            "result": None
        }
        session_log["events"].append(event)
        try:
            result = func(*args, **kwargs)
            event["status"] = "success"
            event["result"] = result
            return result
        except Exception as e:
            event["status"] = "failed"
            log_exception(e, event)
            raise
    return wrapper

# * Функція для логування винятків
def log_exception(e: Exception, event_info=None):
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    session_log["error"] = {
        "type": str(type(e).__name__),
        "message": str(e),
        "traceback": tb_str,
        "failed_in_function": event_info["function"] if event_info else None,
        "step": event_info["step"] if event_info else None,
        "timestamp": str(datetime.datetime.now())
    }
    
    # * Save JSON report
    json_filename = get_unique_filename("error_report", "json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(session_log, f, indent=4, ensure_ascii=False)
    
    # * Згенерувати HTML-звіт
    html_filename = get_unique_filename("error_report", "html")
    generate_html_report(session_log, html_filename)

# * Функція для генерації HTML з даних JSON
def generate_html_report(data, html_filename):
    html_content = f"""
    <html>
    <head>
        <title>Python Error Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h2 {{ color: #333; }}
            .event, .error {{ border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
            .success {{ background-color: #e0f7e0; }}
            .failed {{ background-color: #f8d7da; }}
            pre {{ background-color: #f4f4f4; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Python Session Report</h1>
        <p><strong>Session started:</strong> {data['session_start']}</p>
        <h2>Events</h2>
    """
    for event in data["events"]:
        status_class = "success" if event["status"] == "success" else "failed" if event["status"] == "failed" else ""
        html_content += f"""
        <div class="event {status_class}">
            <p><strong>Step:</strong> {event['step']}</p>
            <p><strong>Function:</strong> {event['function']}</p>
            <p><strong>Args:</strong> {event['args']}</p>
            <p><strong>Kwargs:</strong> {event['kwargs']}</p>
            <p><strong>Timestamp:</strong> {event['timestamp']}</p>
            <p><strong>Status:</strong> {event['status']}</p>
            <p><strong>Result:</strong> {event['result']}</p>
        </div>
        """
    
    if data["error"]:
        html_content += f"""
        <h2>Error</h2>
        <div class="error">
            <p><strong>Type:</strong> {data['error']['type']}</p>
            <p><strong>Message:</strong> {data['error']['message']}</p>
            <p><strong>Failed in function:</strong> {data['error']['failed_in_function']}</p>
            <p><strong>Step:</strong> {data['error']['step']}</p>
            <p><strong>Timestamp:</strong> {data['error']['timestamp']}</p>
            <pre>{data['error']['traceback']}</pre>
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
