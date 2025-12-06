"""
Модуль task1_aggregation.py

Задача 1: Агрегация данных - лучший и худший годы по продажам.
"""

import pandas as pd
from typing import Iterator, Tuple
from lab3.generators import read_csv_chunks, extract_sales_data


def aggregate_sales_by_year(
    chunks: Iterator[pd.DataFrame]
) -> pd.DataFrame:
    """
    Агрегирует продажи по годам.

    Args:
        chunks: Итератор DataFrame с данными о продажах.

    Returns:
        DataFrame с суммарными продажами по годам.
    """
    sales_by_year = {}

    for chunk in chunks:
        # Преобразуем год в целое число
        chunk['Release.Year'] = chunk['Release.Year'].astype(int)
        year_sales = chunk.groupby('Release.Year')['Sales'].sum()
        for year, sales in year_sales.items():
            year_int = int(year)
            if year_int in sales_by_year:
                sales_by_year[year_int] += sales
            else:
                sales_by_year[year_int] = sales

    result_df = pd.DataFrame(
        list(sales_by_year.items()),
        columns=['Year', 'Total_Sales']
    ).sort_values('Year')

    return result_df


def find_best_worst_years(
    sales_df: pd.DataFrame
) -> Tuple[int, int]:
    """
    Находит лучший и худший годы по продажам.

    Args:
        sales_df: DataFrame с продажами по годам.

    Returns:
        Кортеж (лучший_год, худший_год).
    """
    best_year = sales_df.loc[sales_df['Total_Sales'].idxmax(), 'Year']
    worst_year = sales_df.loc[sales_df['Total_Sales'].idxmin(), 'Year']

    return int(best_year), int(worst_year)


def process_task1(filepath: str, chunksize: int = 10000) -> Tuple[pd.DataFrame, int, int]:
    """
    Обрабатывает задачу 1: лучший и худший годы по продажам.

    Args:
        filepath: Путь к CSV файлу.
        chunksize: Размер чанка для чтения.

    Returns:
        Кортеж (DataFrame с продажами по годам, лучший год, худший год).
    """
    csv_chunks = read_csv_chunks(filepath, chunksize)
    sales_chunks = extract_sales_data(csv_chunks)
    sales_by_year = aggregate_sales_by_year(sales_chunks)
    best_year, worst_year = find_best_worst_years(sales_by_year)

    return sales_by_year, best_year, worst_year

