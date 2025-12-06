"""
Скрипт для вычитания двух изображений из файлов
"""
import cv2
import numpy as np
import sys

def subtract_images(image1_path, image2_path, output_path):
    """
    Вычитает второе изображение из первого и сохраняет результат
    
    Args:
        image1_path: путь к первому изображению
        image2_path: путь ко второму изображению (вычитается из первого)
        output_path: путь для сохранения результата
    """
    # Загружаем изображения
    img1 = cv2.imread(image1_path)
    img2 = cv2.imread(image2_path)
    
    if img1 is None:
        print(f"Ошибка: не удалось загрузить {image1_path}")
        return
    
    if img2 is None:
        print(f"Ошибка: не удалось загрузить {image2_path}")
        return
    
    print(f"Изображение 1: {img1.shape}")
    print(f"Изображение 2: {img2.shape}")
    
    # Проверяем размеры
    if img1.shape != img2.shape:
        print("Предупреждение: изображения имеют разные размеры!")
        print("Изменяем размер второго изображения под первое...")
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Вычитаем изображения
    result = np.clip(
        img1.astype(np.float32) - img2.astype(np.float32),
        0, 255
    ).astype(np.uint8)
    
    # Сохраняем результат
    cv2.imwrite(output_path, result)
    print(f"Результат сохранён: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) == 4:
        subtract_images(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Значения по умолчанию
        image1 = "lab2_images/1_Bengal_original.png"
        image2 = "lab2_images/1_Bengal_custom.png"
        output = "lab2_images/result_subtract.png"
        
        print(f"Использование: python subtract_two_images.py <image1> <image2> <output>")
        print(f"\nВычитаем изображения по умолчанию:")
        print(f"  {image1} - {image2}")
        print()
        
        subtract_images(image1, image2, output)
