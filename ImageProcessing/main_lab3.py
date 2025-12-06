"""
main_lab3.py

Точка входа для лабораторной работы №3.

Анализ данных о видеоиграх из CORGIS Dataset.
Вариант 3: Данные о видеоиграх.
"""

import argparse
import os
import sys

from lab3.task1_aggregation import process_task1
from lab3.task2_variance import process_task2
from lab3.task3_time_series import process_task3
from lab3.task4_parquet import process_task4
from lab3.visualization import (
    plot_task1,
    plot_task2,
    plot_task3,
    plot_task4
)


def main() -> None:
    """
    Основная функция для запуска анализа данных о видеоиграх.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Анализ данных о видеоиграх из CORGIS Dataset. "
            "Вариант 3: Лучшие/худшие годы, издатели, рейтинги, корреляция."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--csv-file',
        type=str,
        default='video_games.csv',
        help='Путь к CSV файлу с данными (по умолчанию: video_games.csv)',
    )

    parser.add_argument(
        '--chunksize',
        type=int,
        default=10000,
        help='Размер чанка для чтения CSV (по умолчанию: 10000)',
    )

    parser.add_argument(
        '--window',
        type=int,
        default=3,
        help='Размер окна для скользящего среднего (по умолчанию: 3)',
    )

    parser.add_argument(
        '--skip-task',
        type=int,
        nargs='+',
        choices=[1, 2, 3, 4],
        help='Пропустить выполнение указанных задач (например: --skip-task 4)',
    )

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Ошибка: файл {args.csv_file} не найден.")
        print("Скачайте файл video_games.csv с https://corgis-edu.github.io/corgis/csv/video_games/")
        sys.exit(1)

    skip_tasks = set(args.skip_task) if args.skip_task else set()

    print("=" * 70)
    print("Лабораторная работа №3: Анализ данных о видеоиграх")
    print("=" * 70)
    print(f"CSV файл: {args.csv_file}")
    print(f"Размер чанка: {args.chunksize}")
    print(f"Окно скользящего среднего: {args.window}")
    print()

    # Задача 1: Агрегация - лучший и худший годы по продажам
    if 1 not in skip_tasks:
        print("\n" + "=" * 70)
        print("ЗАДАЧА 1: Лучший и худший годы по продажам")
        print("=" * 70)
        try:
            sales_df, best_year, worst_year = process_task1(args.csv_file, args.chunksize)
            print(f"\nЛучший год по продажам: {best_year}")
            print(f"Худший год по продажам: {worst_year}")
            plot_task1(sales_df, best_year, worst_year)
        except Exception as e:
            print(f"Ошибка при выполнении задачи 1: {e}")
            import traceback
            traceback.print_exc()

    # Задача 2: Дисперсия - издатели с наибольшим/наименьшим разбросом
    if 2 not in skip_tasks:
        print("\n" + "=" * 70)
        print("ЗАДАЧА 2: Издатели с наибольшим/наименьшим разбросом оценок")
        print("=" * 70)
        try:
            top_publishers, bottom_publishers = process_task2(args.csv_file, args.chunksize)
            print("\nИздатели с наибольшим разбросом оценок:")
            print(top_publishers[['Publisher', 'Mean_Score', 'Variance', 'Std_Dev']].to_string(index=False))
            print("\nИздатели с наименьшим разбросом оценок:")
            print(bottom_publishers[['Publisher', 'Mean_Score', 'Variance', 'Std_Dev']].to_string(index=False))
            plot_task2(top_publishers, bottom_publishers)
        except Exception as e:
            print(f"Ошибка при выполнении задачи 2: {e}")
            import traceback
            traceback.print_exc()

    # Задача 3: Временной ряд - количество игр по рейтингам
    if 3 not in skip_tasks:
        print("\n" + "=" * 70)
        print("ЗАДАЧА 3: Количество игр по рейтингам (E, T, M) по годам")
        print("=" * 70)
        try:
            ratings_df = process_task3(args.csv_file, args.chunksize, args.window)
            print(f"\nОбработано {len(ratings_df)} записей")
            print("\nПример данных:")
            print(ratings_df.head(20).to_string(index=False))
            plot_task3(ratings_df)
        except Exception as e:
            print(f"Ошибка при выполнении задачи 3: {e}")
            import traceback
            traceback.print_exc()

    # Задача 4: Дополнительное задание - корреляция с Parquet
    if 4 not in skip_tasks:
        print("\n" + "=" * 70)
        print("ЗАДАЧА 4 (Дополнительное): Корреляция Review.Score и Sales (Parquet)")
        print("=" * 70)
        try:
            parquet_file = args.csv_file.replace('.csv', '.parquet')
            correlation, data_df, csv_time, parquet_time = process_task4(
                args.csv_file,
                parquet_file,
                args.chunksize
            )
            print(f"\nКоэффициент корреляции: {correlation:.4f}")
            print(f"Время чтения CSV: {csv_time:.4f} секунд")
            print(f"Время чтения Parquet: {parquet_time:.4f} секунд")
            plot_task4(data_df, correlation)
        except Exception as e:
            print(f"Ошибка при выполнении задачи 4: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("Анализ завершён!")
    print("=" * 70)


if __name__ == '__main__':
    main()

