"""
Тестовый скрипт для проверки сложения изображений с границами
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lab2.cat_image_processor import CatImageProcessor


def main():
    processor = CatImageProcessor(
        api_type='cat',
        output_dir='lab2_images'
    )

    # Загружаем 2 изображения
    print("Загрузка 2 изображений для сложения...")
    cat_images = processor.fetch_images(limit=2)

    if len(cat_images) < 2:
        print("Не удалось загрузить 2 изображения")
        return

    # Складываем изображения
    print("\nСложение изображений с применением обнаружения границ...")
    processor.add_images(cat_images, indices=[0, 1])


if __name__ == '__main__':
    main()
