"""
Модуль visualization.py

Функции для визуализации результатов анализа данных о видеоиграх.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Tuple


def plot_task1(
    sales_df: pd.DataFrame,
    best_year: int,
    worst_year: int,
    output_path: str = 'lab3_task1_sales_by_year.png'
) -> None:
    """
    Строит график продаж по годам (задача 1).

    Args:
        sales_df: DataFrame с продажами по годам.
        best_year: Лучший год по продажам.
        worst_year: Худший год по продажам.
        output_path: Путь для сохранения графика.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(sales_df['Year'], sales_df['Total_Sales'], marker='o', linewidth=2, markersize=4)
    plt.axvline(x=best_year, color='green', linestyle='--', linewidth=2, label=f'Лучший год: {best_year}')
    plt.axvline(x=worst_year, color='red', linestyle='--', linewidth=2, label=f'Худший год: {worst_year}')
    plt.xlabel('Год', fontsize=12)
    plt.ylabel('Общие продажи', fontsize=12)
    plt.title('Продажи видеоигр по годам', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранён: {output_path}")
    plt.close()


def plot_task2(
    top_publishers: pd.DataFrame,
    bottom_publishers: pd.DataFrame,
    output_path: str = 'lab3_task2_publishers_variance.png'
) -> None:
    """
    Строит график издателей с доверительными интервалами (задача 2).

    Args:
        top_publishers: DataFrame с издателями с наибольшим разбросом.
        bottom_publishers: DataFrame с издателями с наименьшим разбросом.
        output_path: Путь для сохранения графика.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # График для издателей с наибольшим разбросом
    x_pos1 = np.arange(len(top_publishers))
    ax1.barh(x_pos1, top_publishers['Mean_Score'], xerr=[
        top_publishers['Mean_Score'] - top_publishers['CI_Lower'],
        top_publishers['CI_Upper'] - top_publishers['Mean_Score']
    ], capsize=5, alpha=0.7)
    ax1.set_yticks(x_pos1)
    ax1.set_yticklabels(top_publishers['Publisher'], fontsize=10)
    ax1.set_xlabel('Средняя оценка', fontsize=12)
    ax1.set_title('Издатели с наибольшим разбросом оценок\n(с доверительными интервалами 95%)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')

    # График для издателей с наименьшим разбросом
    x_pos2 = np.arange(len(bottom_publishers))
    ax2.barh(x_pos2, bottom_publishers['Mean_Score'], xerr=[
        bottom_publishers['Mean_Score'] - bottom_publishers['CI_Lower'],
        bottom_publishers['CI_Upper'] - bottom_publishers['Mean_Score']
    ], capsize=5, alpha=0.7, color='orange')
    ax2.set_yticks(x_pos2)
    ax2.set_yticklabels(bottom_publishers['Publisher'], fontsize=10)
    ax2.set_xlabel('Средняя оценка', fontsize=12)
    ax2.set_title('Издатели с наименьшим разбросом оценок\n(с доверительными интервалами 95%)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранён: {output_path}")
    plt.close()


def plot_task3(
    ratings_df: pd.DataFrame,
    output_path: str = 'lab3_task3_ratings_by_year.png'
) -> None:
    """
    Строит график количества игр по рейтингам по годам со скользящим средним (задача 3).

    Args:
        ratings_df: DataFrame с данными по годам, рейтингам и скользящим средним.
        output_path: Путь для сохранения графика.
    """
    plt.figure(figsize=(14, 8))

    ratings = ['E', 'T', 'M']
    colors = {'E': 'green', 'T': 'orange', 'M': 'red'}

    for rating in ratings:
        rating_data = ratings_df[ratings_df['Rating'] == rating].copy()
        rating_data = rating_data.sort_values('Year')

        if len(rating_data) > 0:
            plt.plot(
                rating_data['Year'],
                rating_data['Count'],
                marker='o',
                label=f'Рейтинг {rating} (факт)',
                color=colors[rating],
                alpha=0.5,
                linewidth=1,
                markersize=3
            )
            plt.plot(
                rating_data['Year'],
                rating_data['Moving_Average'],
                label=f'Рейтинг {rating} (скользящее среднее)',
                color=colors[rating],
                linewidth=2,
                linestyle='--'
            )

    plt.xlabel('Год', fontsize=12)
    plt.ylabel('Количество игр', fontsize=12)
    plt.title('Количество игр по возрастным рейтингам по годам\n(со скользящим средним, окно=3)', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранён: {output_path}")
    plt.close()


def plot_task4(
    data_df: pd.DataFrame,
    correlation: float,
    output_path: str = 'lab3_task4_correlation.png'
) -> None:
    """
    Строит scatter plot корреляции между Review.Score и Sales (задача 4).

    Args:
        data_df: DataFrame с данными Review.Score и Sales.
        correlation: Коэффициент корреляции.
        output_path: Путь для сохранения графика.
    """
    plt.figure(figsize=(10, 8))

    # Для больших данных используем выборку для визуализации
    if len(data_df) > 10000:
        sample_df = data_df.sample(n=10000, random_state=42)
        print(f"Для визуализации использована выборка из {len(sample_df)} записей")
    else:
        sample_df = data_df

    plt.scatter(
        sample_df['Review.Score'],
        sample_df['Sales'],
        alpha=0.3,
        s=10,
        edgecolors='none'
    )

    plt.xlabel('Оценка игры (Review.Score)', fontsize=12)
    plt.ylabel('Продажи (Sales)', fontsize=12)
    plt.title(
        f'Корреляция между оценкой игры и продажами\n(коэффициент корреляции: {correlation:.4f})',
        fontsize=14,
        fontweight='bold'
    )
    plt.grid(True, alpha=0.3)

    # Добавляем линию тренда
    z = np.polyfit(sample_df['Review.Score'], sample_df['Sales'], 1)
    p = np.poly1d(z)
    plt.plot(
        sample_df['Review.Score'].sort_values(),
        p(sample_df['Review.Score'].sort_values()),
        "r--",
        linewidth=2,
        label=f'Линия тренда (r={correlation:.4f})'
    )
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"График сохранён: {output_path}")
    plt.close()

