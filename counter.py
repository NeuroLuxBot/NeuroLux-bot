import os

COUNTER_FILE = "counter.txt"

def increment_counter():
    # Создаём файл, если его нет
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("0")

    # Считываем текущее значение
    with open(COUNTER_FILE, "r") as f:
        count = int(f.read())

    # Увеличиваем и сохраняем
    count += 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))

    return count
