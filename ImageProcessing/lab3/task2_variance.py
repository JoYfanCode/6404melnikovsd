"""
Модуль task2_variance.py

Задача 2: Дисперсия и доверительный интервал - издатели с наибольшим/наименьшим разбросом оценок.
"""

import pandas as pd
import numpy as np
from typing import Iterator, Tuple
from scipy import stats
from lab3.generators import read_csv_chunks, extract_review_data


def aggregate_reviews_by_publisher(
    chunks: Iterator[pd.DataFrame]
) -> pd.DataFrame:
    """
    Агрегирует оценки по издателям и вычисляет статистику.

    Args:
        chunks: Итератор DataFrame с данными об оценках.

    Returns:
        DataFrame со статистикой по издателям.
    """
    publisher_data = {}

    for chunk in chunks:
        for publisher, group in chunk.groupby('Publisher'):
            scores = group['Review.Score'].values

            if publisher not in publisher_data:
                publisher_data[publisher] = []

            publisher_data[publisher].extend(scores.tolist())

    # Вычисляем статистику для каждого издателя
    results = []
    for publisher, scores in publisher_data.items():
        scores_array = np.array(scores)
        if len(scores_array) > 1:
            mean_score = np.mean(scores_array)
            variance = np.var(scores_array, ddof=1)  # Выборочная дисперсия
            std_dev = np.std(scores_array, ddof=1)
            n = len(scores_array)

            # Доверительный интервал (95%)
            # Используем стандартную ошибку среднего
            sem = std_dev / np.sqrt(n)
            confidence_interval = stats.t.interval(
                0.95,
                n - 1,
                loc=mean_score,
                scale=sem
            )

            results.append({
                'Publisher': publisher,
                'Mean_Score': mean_score,
                'Variance': variance,
                'Std_Dev': std_dev,
                'Count': n,
                'CI_Lower': confidence_interval[0],
                'CI_Upper': confidence_interval[1]
            })

    result_df = pd.DataFrame(results)
    return result_df


def find_top_bottom_publishers(
    stats_df: pd.DataFrame,
    top_n: int = 3
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Находит издателей с наибольшим и наименьшим разбросом оценок.

    Args:
        stats_df: DataFrame со статистикой по издателям.
        top_n: Количество издателей для выбора.

    Returns:
        Кортеж (DataFrame с наибольшим разбросом, DataFrame с наименьшим разбросом).
    """
    # Сортируем по дисперсии
    sorted_df = stats_df.sort_values('Variance', ascending=False)

    top_publishers = sorted_df.head(top_n).copy()
    bottom_publishers = sorted_df.tail(top_n).copy()

    return top_publishers, bottom_publishers


def process_task2(filepath: str, chunksize: int = 10000) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Обрабатывает задачу 2: издатели с наибольшим/наименьшим разбросом оценок.

    Args:
        filepath: Путь к CSV файлу.
        chunksize: Размер чанка для чтения.

    Returns:
        Кортеж (DataFrame с наибольшим разбросом, DataFrame с наименьшим разбросом).
    """
    csv_chunks = read_csv_chunks(filepath, chunksize)
    review_chunks = extract_review_data(csv_chunks)
    publisher_stats = aggregate_reviews_by_publisher(review_chunks)
    top_publishers, bottom_publishers = find_top_bottom_publishers(publisher_stats)

    return top_publishers, bottom_publishers

