from logger_setup import log_function, session_log, logs_folder

# ! ===================== Ваші функції =====================
@log_function
def add(a, b):
    return a + b

@log_function
def minus(a, b):
    return a - b

@log_function
def multiply(a, b):
    return a * b

@log_function
def divide(a, b):
    return a / b

# ! ===================== Виклики функцій =====================
if __name__ == "__main__":
    try:
        add(5, 6)
        minus(5, 2)
        multiply(2, 10)
        divide(5, 0)
    except Exception:
        print("Сталася помилка, звіт JSON та HTML збережено в папці logs")
