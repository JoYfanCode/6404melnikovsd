"""
main_lab4_pipeline.py

Точка входа для дополнительного задания лабораторной работы №4.

Генераторный пайплайн для асинхронной обработки изображений.
"""

import argparse
import asyncio
import sys


def main() -> None:
    """
    Основная функция для запуска генераторного пайплайна.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Генераторный пайплайн для асинхронной загрузки "
            "и параллельной обработки изображений."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Количество изображений для обработки (по умолчанию: 5)',
    )

    parser.add_argument(
        '--api-type',
        choices=['cat'],
        default='cat',
        help='Тип API: cat (по умолчанию: cat)',
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
        default='lab4_pipeline_images',
        help='Директория для сохранения результатов (по умолчанию: lab4_pipeline_images)',
    )

    parser.add_argument(
        '--max-workers',
        type=int,
        default=None,
        help='Максимальное количество процессов для обработки (по умолчанию: количество ядер CPU)',
    )

    args = parser.parse_args()

    try:
        from lab4.async_pipeline_processor import AsyncPipelineProcessor
        
        # Создаём пайплайн-процессор
        processor = AsyncPipelineProcessor(
            api_key=args.api_key,
            api_type=args.api_type,
            output_dir=args.output_dir,
            max_workers=args.max_workers
        )

        # Запускаем генераторный пайплайн
        asyncio.run(processor.run(limit=args.limit))

    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
