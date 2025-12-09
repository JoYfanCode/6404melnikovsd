"""
compare_performance.py

Скрипт для сравнения производительности синхронной (lab2) и асинхронной (lab4) версий.
"""

import time
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def run_sync_version(limit: int) -> float:
    """
    Запускает синхронную версию (lab2) и возвращает время выполнения.
    
    Args:
        limit: Количество изображений для обработки.
    
    Returns:
        Время выполнения в секундах.
    """
    from lab2.cat_image_processor import CatImageProcessor
    
    print("=" * 60)
    print("СИНХРОННАЯ ВЕРСИЯ (LAB2)")
    print("=" * 60)
    
    start_time = time.perf_counter()
    
    processor = CatImageProcessor(
        api_type='cat',
        output_dir='lab2_images_test'
    )
    
    # Загружаем и обрабатываем изображения
    cat_images = processor.fetch_images(limit=limit)
    processor.process_images(cat_images)
    
    elapsed_time = time.perf_counter() - start_time
    
    print(f"\nВремя выполнения синхронной версии: {elapsed_time:.4f} секунд")
    print("=" * 60)
    print()
    
    return elapsed_time


async def run_async_version(limit: int) -> float:
    """
    Запускает асинхронную версию (lab4) и возвращает время выполнения.
    
    Args:
        limit: Количество изображений для обработки.
    
    Returns:
        Время выполнения в секундах.
    """
    from lab4.async_cat_image_processor import AsyncCatImageProcessor
    
    print("=" * 60)
    print("АСИНХРОННАЯ ВЕРСИЯ (LAB4)")
    print("=" * 60)
    
    start_time = time.perf_counter()
    
    processor = AsyncCatImageProcessor(
        api_type='cat',
        output_dir='lab4_images_test'
    )
    
    await processor.run(limit=limit)
    
    elapsed_time = time.perf_counter() - start_time
    
    print(f"\nВремя выполнения асинхронной версии: {elapsed_time:.4f} секунд")
    print("=" * 60)
    print()
    
    return elapsed_time


def main():
    """
    Основная функция для сравнения производительности.
    """
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(
        description="Сравнение производительности синхронной и асинхронной версий"
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Количество изображений для обработки (по умолчанию: 5)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print(f"Количество изображений: {args.limit}")
    print("=" * 60)
    print()
    
    try:
        # Запускаем синхронную версию
        sync_time = run_sync_version(args.limit)
        
        # Запускаем асинхронную версию
        async_time = asyncio.run(run_async_version(args.limit))
        
        # Выводим результаты сравнения
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
        print("=" * 60)
        print(f"Синхронная версия (lab2):  {sync_time:.4f} секунд")
        print(f"Асинхронная версия (lab4): {async_time:.4f} секунд")
        print(f"Ускорение: {sync_time / async_time:.2f}x")
        print(f"Выигрыш во времени: {sync_time - async_time:.4f} секунд")
        print("=" * 60)
        
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
