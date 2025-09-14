import json
import datetime
from pathlib import Path
import traceback
import sys
import linecache

# TODO ===================== Налаштування логів =====================
logs_folder = Path("logs")
logs_folder.mkdir(parents=True, exist_ok=True)

# * Глобальний журнал сесії
session_log = {
    "початок_сесії": str(datetime.datetime.now()),
    "події": [],
    "помилка": None
}

# TODO ===================== Декоратор для логування =====================
def log_function(func):
    def wrapper(*args, **kwargs):
        step = len(session_log["події"]) + 1
        event = {
            "крок": step,
            "функція": func.__name__,
            "аргументи": args,
            "ключові_аргументи": kwargs,
            "час": str(datetime.datetime.now()),
            "статус": "початок",
            "результат": None
        }
        session_log["події"].append(event)
        print(f"[INFO] Крок {step} - Функція '{func.__name__}' запущена з аргументами {args}, {kwargs}")
        try:
            result = func(*args, **kwargs)
            event["статус"] = "успіх"
            event["результат"] = result
            print(f"[SUCCESS] Крок {step} - Функція '{func.__name__}' успішно виконана: {result}")
            return result
        except Exception as e:
            event["статус"] = "помилка"
            log_exception(e, event)
            print(f"[ERROR] Крок {step} - Функція '{func.__name__}' завершилася помилкою: {e}")
            raise
    return wrapper

# TODO ===================== Логування винятків =====================
def log_exception(e: Exception, event_info=None):
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    # TODO Отримуємо останній фрейм
    last_tb = exc_tb
    while last_tb.tb_next:
        last_tb = last_tb.tb_next
    frame = last_tb.tb_frame
    lineno = last_tb.tb_lineno
    filename = frame.f_code.co_filename
    locals_vars = {k: repr(v) for k, v in frame.f_locals.items()}

    # TODO Фрагмент коду навколо помилки
    start = max(1, lineno - 3)
    end = lineno + 3
    code_fragment = []
    for i in range(start, end + 1):
        line = linecache.getline(filename, i).rstrip()
        code_fragment.append({
            "рядок": i,
            "код": line,
            "помилка": i == lineno
        })

    session_log["помилка"] = {
        "тип": str(type(e).__name__),
        "повідомлення": str(e),
        "traceback": tb_str,
        "файл": filename,
        "рядок": lineno,
        "фрагмент_коду": code_fragment,
        "локальні_змінні": locals_vars,
        "у_якій_функції": event_info["функція"] if event_info else None,
        "крок": event_info["крок"] if event_info else None,
        "час": str(datetime.datetime.now())
    }

    # TODO Зберегти JSON
    json_filename = logs_folder / f"звіт_помилки_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(session_log, f, indent=4, ensure_ascii=False)

    # Згенерувати HTML
    html_filename = logs_folder / f"звіт_помилки_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    generate_html_report(session_log, html_filename, exc_tb)

# TODO ===================== Генерація HTML =====================
def generate_html_report(data, html_filename, tb=None):
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Звіт сесії Python</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h2 {{ color: #333; }}
            .event, .error {{ border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
            .успіх {{ background-color: #e0f7e0; }}
            .помилка {{ background-color: #f8d7da; }}
            pre {{ background-color: #f4f4f4; padding: 10px; overflow-x: auto; }}
            .рядок-коду {{ background-color: #f0f0f0; padding: 2px 5px; display:block; }}
            .рядок-помилки {{ background-color: #ffdddd; }}
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
            <p><strong>Файл:</strong> {data['помилка']['файл']}</p>
            <p><strong>Рядок:</strong> {data['помилка']['рядок']}</p>
            <p><strong>Функція:</strong> {data['помилка']['у_якій_функції']}</p>
            <p><strong>Крок:</strong> {data['помилка']['крок']}</p>
            <p><strong>Час:</strong> {data['помилка']['час']}</p>
            <h3>Локальні змінні:</h3>
            <pre>{data['помилка']['локальні_змінні']}</pre>
            <h3>Traceback:</h3>
            <pre>{data['помилка']['traceback']}</pre>
            <h3>Фрагмент коду навколо помилки:</h3>
            <pre>
        """
        for line in data['помилка']['фрагмент_коду']:
            cls = "рядок-помилки" if line["помилка"] else ""
            html_content += f'<span class="рядок-коду {cls}">{line["рядок"]}: {line["код"]}</span>'
        html_content += "</pre></div>"
    
    html_content += "</body></html>"
    
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
