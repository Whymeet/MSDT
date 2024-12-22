import csv
import re


# Регулярные выражения для валидации данных
VALIDATION_PATTERNS = {
    "email"     : r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "height"    : r"^([0-2](\.\d{2})?)$",
    "inn"       : r"^\d{12}$",
    "passport"  : r"^\d{2}\s\d{2}\s\d{6}$",
    "occupation": r"^[а-яА-ЯёЁa-zA-Z\s\-]+$",
    "latitude"  : r"^-?(90(\.0+)?|[1-8]?\d(\.\d+)?)$",
    "hex_color" : r"^#[0-9a-fA-F]{6}$",
    "issn"      : r"^\d{4}-\d{4}$",
    "uuid"      : r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    "time"      : r"^([01]?\d|2[0-3]):[0-5]\d:[0-5]\d\.\d{6}$"
}

def validate_row(row, patterns):
    """
    Проверяет строку CSV на соответствие регулярным выражениям.

    :param row: Список значений строки CSV.
    :param patterns: Словарь с регулярными выражениями для проверки.
    :return: Список индексов столбцов с ошибками.
    """
    errors = []
    for idx, (key, pattern) in enumerate(patterns.items()):
        if not re.match(pattern, row[idx]):
            errors.append(idx)
    return errors

def process_csv(file_path, patterns):
    """
    Обрабатывает CSV-файл, выполняя валидацию строк.

    :param file_path: Путь к CSV-файлу.
    :param patterns: Словарь с регулярными выражениями для проверки.
    :return: Список номеров строк с ошибками.
    """
    invalid_rows = []
    with open(file_path, newline='', encoding='utf-16') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)  # Пропустить заголовок
        for row_num, row in enumerate(reader, start=0):
            if validate_row(row, patterns):
                invalid_rows.append(row_num)
    return invalid_rows