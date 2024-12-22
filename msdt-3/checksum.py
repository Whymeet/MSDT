import json
import hashlib
from typing import List
from validator import *

"""
В этом модуле обитают функции, необходимые для автоматизированной проверки результатов ваших трудов.
"""


def calculate_checksum(row_numbers: List[int]) -> str:
    """
    Вычисляет md5 хеш от списка целочисленных значений.

    ВНИМАНИЕ, ВАЖНО! Чтобы сумма получилась корректной, считать, что первая строка с данными csv-файла имеет номер 0
    Другими словами: В исходном csv 1я строка - заголовки столбцов, 2я и остальные - данные.
    Соответственно, считаем что у 2 строки файла номер 0, у 3й - номер 1 и так далее.

    :param row_numbers: список целочисленных номеров строк csv-файла, на которых были найдены ошибки валидации
    :return: md5 хеш для проверки через github action
    """
    row_numbers.sort()
    return hashlib.md5(json.dumps(row_numbers).encode('utf-8')).hexdigest()



def serialize_result(variant, checksum, result_file):
    """
    Записывает результаты в JSON-файл.

    :param variant: Номер варианта.
    :param checksum: Контрольная сумма.
    :param result_file: Путь к файлу result.json.
    """
    result_data = {
        "variant": variant,
        "checksum": checksum
    }
    with open(result_file, 'w', encoding='utf-8') as file:
        json.dump(result_data, file, ensure_ascii=False, indent=4)

def main():
    """
    Основная функция выполнения валидации и записи результатов.
    """
    file_path = "87.csv"
    result_file = "result.json"
    variant = 87

    # Валидация данных
    invalid_rows = process_csv(file_path, VALIDATION_PATTERNS)

    # Подсчет контрольной суммы
    checksum = calculate_checksum(invalid_rows)

    # Запись результатов
    serialize_result(variant, checksum, result_file)

if __name__ == "__main__":
    main()