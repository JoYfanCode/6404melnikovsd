"""
main_lab2.py

Точка входа для лабораторной работы №2.

Обработка изображений животных через API.
"""

import argparse
import sys

from lab2.cat_image_processor import CatImageProcessor


def main() -> None:
    """
    Основная функция для запуска программы.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Обработка изображений животных через API "
            "с выделением контуров."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=1,
        help='Количество изображений для обработки (по умолчанию: 1)',
    )

    parser.add_argument(
        '--api-type',
        choices=['cat', 'dog'],
        default='cat',
        help='Тип API: cat или dog (по умолчанию: cat)',
    )

    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='API ключ (по умолчанию берётся из .env файла)',
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='lab2_images',
        help='Директория для сохранения результатов (по умолчанию: lab2_images)',
    )

    args = parser.parse_args()

    try:
        # Создаём процессор
        processor = CatImageProcessor(
            api_key=args.api_key,
            api_type=args.api_type,
            output_dir=args.output_dir
        )

        # Запускаем обработку
        processor.run(limit=args.limit)

    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

