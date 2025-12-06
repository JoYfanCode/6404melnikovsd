"""
Модуль task4_parquet.py

Дополнительное задание: Корреляция между Review.Score и Sales с использованием Parquet.
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
import os
import time
from typing import Tuple


def csv_to_parquet(
    csv_filepath: str,
    parquet_filepath: str,
    chunksize: int = 10000
) -> None:
    """
    Конвертирует CSV файл в Parquet формат.

    Args:
        csv_filepath: Путь к CSV файлу.
        parquet_filepath: Путь для сохранения Parquet файла.
        chunksize: Размер чанка для чтения.
    """
    if os.path.exists(parquet_filepath):
        print(f"Parquet файл {parquet_filepath} уже существует, пропускаем конвертацию.")
        return

    print(f"Конвертация CSV в Parquet...")
    chunks = []
    total_rows = 0

    for chunk in pd.read_csv(csv_filepath, chunksize=chunksize):
        chunks.append(chunk)
        total_rows += len(chunk)

    print(f"Прочитано {total_rows} строк из CSV")

    # Объединяем все чанки
    full_df = pd.concat(chunks, ignore_index=True)

    # Сохраняем в Parquet
    table = pa.Table.from_pandas(full_df)
    pq.write_table(table, parquet_filepath)
    print(f"Parquet файл сохранён: {parquet_filepath}")


def compare_read_speed(
    csv_filepath: str,
    parquet_filepath: str
) -> Tuple[float, float]:
    """
    Сравнивает скорость чтения CSV и Parquet файлов.

    Args:
        csv_filepath: Путь к CSV файлу.
        parquet_filepath: Путь к Parquet файлу.

    Returns:
        Кортеж (время_чтения_csv, время_чтения_parquet) в секундах.
    """
    # Чтение CSV
    print("Чтение CSV файла...")
    start_time = time.perf_counter()
    csv_df = pd.read_csv(csv_filepath)
    csv_time = time.perf_counter() - start_time
    print(f"CSV: {len(csv_df)} строк за {csv_time:.4f} секунд")

    # Чтение Parquet
    print("Чтение Parquet файла...")
    start_time = time.perf_counter()
    parquet_df = pd.read_parquet(parquet_filepath)
    parquet_time = time.perf_counter() - start_time
    print(f"Parquet: {len(parquet_df)} строк за {parquet_time:.4f} секунд")

    speedup = csv_time / parquet_time if parquet_time > 0 else 0
    print(f"Ускорение чтения Parquet: {speedup:.2f}x")

    return csv_time, parquet_time


def calculate_correlation_parquet(
    parquet_filepath: str
) -> Tuple[float, pd.DataFrame]:
    """
    Вычисляет корреляцию между Metrics.Review Score и Metrics.Sales из Parquet файла.

    Читает только необходимые столбцы для оптимизации.

    Args:
        parquet_filepath: Путь к Parquet файлу.

    Returns:
        Кортеж (коэффициент корреляции, DataFrame с данными).
    """
    print("Чтение данных из Parquet (только нужные столбцы)...")
    parquet_file = pq.ParquetFile(parquet_filepath)

    # Читаем только нужные столбцы
    columns = ['Metrics.Review Score', 'Metrics.Sales']
    df = parquet_file.read(columns=columns).to_pandas()

    # Переименовываем для удобства
    df = df.rename(columns={
        'Metrics.Review Score': 'Review.Score',
        'Metrics.Sales': 'Sales'
    })

    # Очистка данных
    df = df.dropna(subset=['Review.Score', 'Sales'])
    df = df[
        (df['Review.Score'] >= 0) &
        (df['Review.Score'] <= 100) &
        (df['Sales'] >= 0)
    ]

    # Вычисление корреляции
    correlation = df['Review.Score'].corr(df['Sales'])

    print(f"Корреляция между Review.Score и Sales: {correlation:.4f}")
    print(f"Обработано {len(df)} записей")

    return correlation, df


def process_task4(
    csv_filepath: str,
    parquet_filepath: str = 'video_games.parquet',
    chunksize: int = 10000
) -> Tuple[float, pd.DataFrame, float, float]:
    """
    Обрабатывает дополнительное задание: корреляция с использованием Parquet.

    Args:
        csv_filepath: Путь к CSV файлу.
        parquet_filepath: Путь для сохранения Parquet файла.
        chunksize: Размер чанка для чтения.

    Returns:
        Кортеж (корреляция, DataFrame с данными, время_чтения_csv, время_чтения_parquet).
    """
    # Конвертация в Parquet
    csv_to_parquet(csv_filepath, parquet_filepath, chunksize)

    # Сравнение скорости чтения
    csv_time, parquet_time = compare_read_speed(csv_filepath, parquet_filepath)

    # Вычисление корреляции из Parquet
    correlation, data_df = calculate_correlation_parquet(parquet_filepath)

    return correlation, data_df, csv_time, parquet_time

