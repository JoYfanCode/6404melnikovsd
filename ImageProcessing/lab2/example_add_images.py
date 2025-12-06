"""
example_add_images.py

Пример использования сложения изображений в лабораторной работе №2.
"""

from lab2.cat_image_processor import CatImageProcessor


def main():
    """
    Демонстрация сложения двух изображений.
    """
    # Создаём процессор
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

    print("\n" + "=" * 50)
    print("Информация о загруженных изображениях:")
    print("=" * 50)
    for i, img in enumerate(cat_images):
        print(f"Изображение {i}: {img}")

    # Складываем изображения
    print("\n" + "=" * 50)
    print("Сложение изображений")
    print("=" * 50)
    
    # Вариант 1: Использование оператора +
    print("\nВариант 1: Использование оператора +")
    try:
        result = cat_images[0] + cat_images[1]
        print(f"Результат: {result}")
        
        # Сохраняем результат
        import cv2
        import os
        output_path = os.path.join(
            processor.output_dir,
            "summed_example.png"
        )
        cv2.imwrite(output_path, result.image)
        print(f"Результат сохранён: {output_path}")
    except ValueError as e:
        print(f"Ошибка: {e}")
        print("Изображения имеют разные размеры, нельзя сложить напрямую")

    # Вариант 2: Использование метода процессора
    print("\nВариант 2: Использование метода процессора")
    processor.add_images(cat_images, indices=[0, 1])


if __name__ == '__main__':
    main()

