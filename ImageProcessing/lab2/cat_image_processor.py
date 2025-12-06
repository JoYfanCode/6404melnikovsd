"""
Модуль cat_image_processor.py

Класс CatImageProcessor для работы с API и обработки изображений животных.
"""

import os
import requests
import numpy as np
import cv2
from typing import List, Optional
from dotenv import load_dotenv

from lab2.cat_image import CatImage, ColorCatImage, GrayscaleCatImage
from lab2.utils import timing_decorator

load_dotenv()

class CatImageProcessor:
    """
    Класс для работы с API, обработки и сохранения изображений животных.

    Инкапсулирует функционал работы с API, а также управляет процессом
    обработки и сохранения скачанных изображений.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_type: str = 'cat',
        output_dir: str = 'lab2_images'
    ) -> None:
        """
        Инициализация процессора изображений.

        Args:
            api_key: API ключ для доступа к API. Если None, берётся из .env.
            api_type: Тип API (только 'cat').
            output_dir: Директория для сохранения результатов.
        """
        self._api_key = api_key or os.getenv('API_KEY')
        if not self._api_key:
            raise ValueError(
                "API_KEY не найден. Укажите его в .env файле или "
                "передайте при создании CatImageProcessor."
            )

        self._api_type = api_type.lower()
        if self._api_type == 'cat':
            self._api_base_url = 'https://api.thecatapi.com/v1'
        else:
            raise ValueError("api_type должен быть 'cat'")

        self._output_dir = output_dir
        self._ensure_output_dir()

    @property
    def api_key(self) -> str:
        """Возвращает API ключ."""
        return self._api_key

    @property
    def api_type(self) -> str:
        """Возвращает тип API."""
        return self._api_type

    @property
    def output_dir(self) -> str:
        """Возвращает директорию для сохранения результатов."""
        return self._output_dir

    def _ensure_output_dir(self) -> None:
        """Создаёт директорию для сохранения, если её нет."""
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
            print(f"Создана директория: {self._output_dir}")

    @timing_decorator
    def fetch_images(
        self,
        limit: int = 1
    ) -> List[CatImage]:
        """
        Загружает изображения животных через API.

        Args:
            limit: Количество изображений для загрузки.

        Returns:
            Список объектов CatImage с загруженными изображениями.
        """
        print(f"Загрузка {limit} изображений из {self._api_type} API...")

        url = f"{self._api_base_url}/images/search"
        params = {
            'limit': limit,
            'has_breeds': True,
            'api_key': self._api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            cat_images = []
            for item in data:
                image_url = item.get('url')
                breed_info = item.get('breeds', [{}])[0]
                breed_name = breed_info.get('name', 'unknown')

                # Загружаем изображение
                img_array = self._download_image(image_url)

                # Определяем тип изображения и создаём объект
                if len(img_array.shape) == 3:
                    cat_image = ColorCatImage(img_array, image_url, breed_name)
                else:
                    cat_image = GrayscaleCatImage(img_array, image_url, breed_name)

                cat_images.append(cat_image)
                print(f"Загружено изображение: {breed_name}")

            return cat_images

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            raise
        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            raise

    @timing_decorator
    def _download_image(self, url: str) -> np.ndarray:
        """
        Скачивает изображение по URL и преобразует в numpy массив.

        Args:
            url: URL изображения.

        Returns:
            Массив numpy с изображением.
        """
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Преобразуем байты в numpy массив
        image_array = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError(f"Не удалось декодировать изображение из {url}")

        return image

    @timing_decorator
    def process_images(self, cat_images: List[CatImage]) -> None:
        """
        Обрабатывает список изображений и сохраняет результаты.

        Args:
            cat_images: Список изображений для обработки.
        """
        print(f"Обработка {len(cat_images)} изображений...")

        for idx, cat_image in enumerate(cat_images, start=1):
            print(f"\nОбработка изображения {idx}/{len(cat_images)}: {cat_image.breed}")

            # Определяем безопасное имя файла для породы
            safe_breed_name = self._sanitize_filename(cat_image.breed)

            # Сохраняем исходное изображение
            original_path = os.path.join(
                self._output_dir,
                f"{idx}_{safe_breed_name}_original.png"
            )
            cv2.imwrite(original_path, cat_image.image)
            print(f"Сохранено исходное изображение: {original_path}")

            # Обработка пользовательским методом
            custom_edges = cat_image.detect_edges_custom()
            custom_path = os.path.join(
                self._output_dir,
                f"{idx}_{safe_breed_name}_custom.png"
            )
            cv2.imwrite(custom_path, custom_edges)
            print(f"Сохранено изображение (custom): {custom_path}")

            # Обработка библиотечным методом
            library_edges = cat_image.detect_edges_library()
            library_path = os.path.join(
                self._output_dir,
                f"{idx}_{safe_breed_name}_library.png"
            )
            cv2.imwrite(library_path, library_edges)
            print(f"Сохранено изображение (library): {library_path}")

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Очищает имя файла от недопустимых символов.

        Args:
            filename: Исходное имя файла.

        Returns:
            Безопасное имя файла.
        """
        # Заменяем недопустимые символы на подчёркивания
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Удаляем пробелы в начале и конце
        filename = filename.strip()
        # Если имя пустое, используем 'unknown'
        if not filename:
            filename = 'unknown'
        return filename

    @timing_decorator
    def add_images(
        self,
        cat_images: List[CatImage],
        indices: Optional[List[int]] = None
    ) -> None:
        """
        Складывает два или более изображений и сохраняет результат.

        Args:
            cat_images: Список изображений для сложения.
            indices: Индексы изображений для сложения (по умолчанию первые два).
        """
        if len(cat_images) < 2:
            print("Для сложения нужно минимум 2 изображения")
            return

        if indices is None:
            indices = [0, 1]

        if len(indices) < 2:
            print("Нужно указать минимум 2 индекса для сложения")
            return

        if max(indices) >= len(cat_images):
            print(f"Ошибка: индекс {max(indices)} выходит за границы списка (всего {len(cat_images)} изображений)")
            return

        try:
            # Берём первое изображение
            result = cat_images[indices[0]]

            # Складываем с остальными
            for idx in indices[1:]:
                print(f"Сложение изображения {indices[0]} ({result.breed}) с изображением {idx} ({cat_images[idx].breed})...")
                
                # Проверяем размеры
                if result.image.shape != cat_images[idx].image.shape:
                    print(f"Предупреждение: изображения имеют разные размеры!")
                    print(f"  Изображение {indices[0]}: {result.image.shape}")
                    print(f"  Изображение {idx}: {cat_images[idx].image.shape}")
                    print("Пропускаем это изображение...")
                    continue

                result = result + cat_images[idx]

            # Сохраняем результат сложения
            safe_name = self._sanitize_filename(result.breed)
            result_path = os.path.join(
                self._output_dir,
                f"summed_{safe_name}.png"
            )
            cv2.imwrite(result_path, result.image)
            print(f"Результат сложения сохранён: {result_path}")
            print(f"Результирующее изображение: {result}")

            # Применяем обнаружение границ к результату
            print("\nПрименение обнаружения границ к результату сложения...")
            edges = result.detect_edges_custom()
            edges_path = os.path.join(
                self._output_dir,
                f"summed_{safe_name}_edges.png"
            )
            cv2.imwrite(edges_path, edges)
            print(f"Результат с границами сохранён: {edges_path}")

        except Exception as e:
            print(f"Ошибка при сложении изображений: {e}")
            import traceback
            traceback.print_exc()

    @timing_decorator
    def run(self, limit: int = 1) -> None:
        """
        Основной метод для запуска обработки.

        Загружает изображения, обрабатывает их и сохраняет результаты.

        Args:
            limit: Количество изображений для обработки.
        """
        print(f"=== Начало обработки {limit} изображений ===")
        print(f"API: {self._api_type}")
        print(f"Директория сохранения: {self._output_dir}\n")

        # Загружаем изображения
        cat_images = self.fetch_images(limit=limit)

        # Обрабатываем и сохраняем
        self.process_images(cat_images)

        # Если загружено 2+ изображения, демонстрируем сложение
        if len(cat_images) >= 2:
            print("\n" + "=" * 50)
            print("Демонстрация сложения изображений")
            print("=" * 50)
            self.add_images(cat_images)

        print(f"\n=== Обработка завершена ===")
        print(f"Результаты сохранены в: {self._output_dir}")

