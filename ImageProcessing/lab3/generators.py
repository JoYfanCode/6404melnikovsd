"""
Модуль generators.py

Генераторы для пайплайна обработки данных о видеоиграх.
"""

import pandas as pd
from typing import Iterator, Optional
import os


def read_csv_chunks(
    filepath: str,
    chunksize: int = 10000
) -> Iterator[pd.DataFrame]:
    """
    Генератор для чтения CSV файла по частям.

    Args:
        filepath: Путь к CSV файлу.
        chunksize: Размер чанка для чтения.

    Yields:
        DataFrame с очередной порцией данных.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл {filepath} не найден")

    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        yield chunk


def extract_sales_data(
    chunks: Iterator[pd.DataFrame]
) -> Iterator[pd.DataFrame]:
    """
    Генератор для извлечения данных о продажах.

    Извлекает необходимые столбцы: Release.Year, Sales.

    Args:
        chunks: Итератор DataFrame из read_csv_chunks.

    Yields:
        DataFrame с извлечёнными данными о продажах.
    """
    for chunk in chunks:
        required_columns = ['Release.Year', 'Sales']
        if all(col in chunk.columns for col in required_columns):
            extracted = chunk[required_columns].copy()
            # Удаляем строки с пропусками
            extracted = extracted.dropna(subset=required_columns)
            # Фильтруем валидные годы и продажи
            extracted = extracted[
                (extracted['Release.Year'] > 0) &
                (extracted['Sales'] >= 0)
            ]
            if not extracted.empty:
                yield extracted


def extract_review_data(
    chunks: Iterator[pd.DataFrame]
) -> Iterator[pd.DataFrame]:
    """
    Генератор для извлечения данных об оценках.

    Извлекает столбцы: Publisher, Review.Score.

    Args:
        chunks: Итератор DataFrame из read_csv_chunks.

    Yields:
        DataFrame с извлечёнными данными об оценках.
    """
    for chunk in chunks:
        required_columns = ['Publisher', 'Review.Score']
        if all(col in chunk.columns for col in required_columns):
            extracted = chunk[required_columns].copy()
            extracted = extracted.dropna(subset=required_columns)
            # Фильтруем валидные оценки (обычно 0-100)
            extracted = extracted[
                (extracted['Review.Score'] >= 0) &
                (extracted['Review.Score'] <= 100)
            ]
            if not extracted.empty:
                yield extracted


def extract_rating_data(
    chunks: Iterator[pd.DataFrame]
) -> Iterator[pd.DataFrame]:
    """
    Генератор для извлечения данных о рейтингах.

    Извлекает столбцы: Release.Year, Rating.

    Args:
        chunks: Итератор DataFrame из read_csv_chunks.

    Yields:
        DataFrame с извлечёнными данными о рейтингах.
    """
    for chunk in chunks:
        required_columns = ['Release.Year', 'Rating']
        if all(col in chunk.columns for col in required_columns):
            extracted = chunk[required_columns].copy()
            extracted = extracted.dropna(subset=required_columns)
            # Фильтруем только нужные рейтинги: E, T, M
            extracted = extracted[extracted['Rating'].isin(['E', 'T', 'M'])]
            extracted = extracted[extracted['Release.Year'] > 0]
            if not extracted.empty:
                yield extracted


def extract_correlation_data(
    chunks: Iterator[pd.DataFrame]
) -> Iterator[pd.DataFrame]:
    """
    Генератор для извлечения данных для корреляции.

    Извлекает столбцы: Review.Score, Sales.

    Args:
        chunks: Итератор DataFrame из read_csv_chunks.

    Yields:
        DataFrame с извлечёнными данными для корреляции.
    """
    for chunk in chunks:
        required_columns = ['Review.Score', 'Sales']
        if all(col in chunk.columns for col in required_columns):
            extracted = chunk[required_columns].copy()
            extracted = extracted.dropna(subset=required_columns)
            extracted = extracted[
                (extracted['Review.Score'] >= 0) &
                (extracted['Review.Score'] <= 100) &
                (extracted['Sales'] >= 0)
            ]
            if not extracted.empty:
                yield extracted

