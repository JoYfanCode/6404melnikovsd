"""
Модуль task3_time_series.py

Задача 3: Изменение значения во времени и скользящее среднее -
количество игр по рейтингам (E, T, M) по годам.
"""

import pandas as pd
from typing import Iterator
from lab3.generators import read_csv_chunks, extract_rating_data


def aggregate_ratings_by_year(
    chunks: Iterator[pd.DataFrame]
) -> pd.DataFrame:
    """
    Агрегирует количество игр по рейтингам и годам.

    Args:
        chunks: Итератор DataFrame с данными о рейтингах.

    Returns:
        DataFrame с количеством игр по годам и рейтингам.
    """
    rating_data = {}

    for chunk in chunks:
        grouped = chunk.groupby(['Release.Year', 'Rating']).size().reset_index(name='Count')

        for _, row in grouped.iterrows():
            year = int(row['Release.Year'])
            rating = row['Rating']
            count = row['Count']

            key = (year, rating)
            if key in rating_data:
                rating_data[key] += count
            else:
                rating_data[key] = count

    # Преобразуем в DataFrame
    result_list = [
        {'Year': year, 'Rating': rating, 'Count': count}
        for (year, rating), count in rating_data.items()
    ]

    result_df = pd.DataFrame(result_list)
    result_df = result_df.sort_values('Year')

    return result_df


def calculate_moving_average(
    df: pd.DataFrame,
    window: int = 3
) -> pd.DataFrame:
    """
    Вычисляет скользящее среднее для каждого рейтинга.

    Args:
        df: DataFrame с данными по годам и рейтингам.
        window: Размер окна для скользящего среднего.

    Returns:
        DataFrame с добавленным столбцом Moving_Average.
    """
    result_df = df.copy()

    for rating in ['E', 'T', 'M']:
        rating_data = result_df[result_df['Rating'] == rating].copy()
        rating_data = rating_data.sort_values('Year')

        if len(rating_data) > 0:
            rating_data['Moving_Average'] = (
                rating_data['Count']
                .rolling(window=window, min_periods=1)
                .mean()
            )

            result_df.loc[result_df['Rating'] == rating, 'Moving_Average'] = (
                rating_data['Moving_Average'].values
            )

    return result_df


def process_task3(filepath: str, chunksize: int = 10000, window: int = 3) -> pd.DataFrame:
    """
    Обрабатывает задачу 3: количество игр по рейтингам по годам со скользящим средним.

    Args:
        filepath: Путь к CSV файлу.
        chunksize: Размер чанка для чтения.
        window: Размер окна для скользящего среднего.

    Returns:
        DataFrame с данными по годам, рейтингам и скользящим средним.
    """
    csv_chunks = read_csv_chunks(filepath, chunksize)
    rating_chunks = extract_rating_data(csv_chunks)
    ratings_by_year = aggregate_ratings_by_year(rating_chunks)
    result_df = calculate_moving_average(ratings_by_year, window)

    return result_df

