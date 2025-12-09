"""
Модуль async_cat_image_processor.py

Асинхронный класс для работы с API и параллельной обработки изображений.
"""

import os
import asyncio
import aiohttp
import aiofiles
import numpy as np
import cv2
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor
import time
import multiprocessing as mp

from lab2.cat_image import CatImage, ColorCatImage, GrayscaleCatImage

load_dotenv()


def apply_convolution_worker(
    image_data: bytes,
    image_index: int,
    breed: str,
    image_url: str
) -> Tuple[int, np.ndarray, np.ndarray, str]:
    """
    Функция для параллельной обработки изображения (применение свёртки).
    
    Выполняется в отдельном процессе.
    
    Args:
        image_data: Байты изображения.
        image_index: Порядковый номер изображения.
        breed: Порода животного.
        image_url: URL изображения.
    
    Returns:
        Кортеж (индекс, custom_edges, library_edges, breed).
    """
    pid = os.getpid()
    print(f"Convolution for image {image_index} started (PID {pid})")
    
    # Декодируем изображение
    image_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # Создаём объект CatImage
    if len(image.shape) == 3:
        cat_image = ColorCatImage(image, image_url, breed)
    else:
        cat_image = GrayscaleCatImage(image, image_url, breed)
    
    # Применяем обработку
    custom_edges = cat_image.detect_edges_custom()
    library_edges = cat_image.detect_edges_library()
    
    print(f"Convolution for image {image_index} finished (PID {pid})")
    
    return image_index, custom_edges, library_edges, breed


class AsyncCatImageProcessor:
    """
    Асинхронный класс для работы с API и параллельной обработки изображений.
    
    Использует:
    - aiohttp для асинхронной загрузки изображений
    - aiofiles для асинхронного сохранения файлов
    - ProcessPoolExecutor для параллельной обработки изображений
    """
    
    def __init__(
        self,
        api_key: str = None,
        api_type: str = 'cat',
        output_dir: str = 'lab4_images',
        max_workers: int = None
    ) -> None:
        """
        Инициализация асинхронного процессора.
        
        Args:
            api_key: API ключ для доступа к API.
            api_type: Тип API (только 'cat').
            output_dir: Директория для сохранения результатов.
            max_workers: Максимальное количество процессов для обработки.
        """
        self._api_key = api_key or os.getenv('API_KEY')
        if not self._api_key:
            raise ValueError(
                "API_KEY не найден. Укажите его в .env файле."
            )
        
        self._api_type = api_type.lower()
        if self._api_type == 'cat':
            self._api_base_url = 'https://api.thecatapi.com/v1'
        else:
            raise ValueError("api_type должен быть 'cat'")
        
        self._output_dir = output_dir
        self._max_workers = max_workers or mp.cpu_count()
        
    async def _ensure_output_dir(self) -> None:
        """Создаёт директорию для сохранения, если её нет."""
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
            print(f"Создана директория: {self._output_dir}")
    
    async def _fetch_image_urls(
        self,
        session: aiohttp.ClientSession,
        limit: int
    ) -> List[Dict]:
        """
        Получает список URL изображений из API.
        
        Args:
            session: Асинхронная сессия aiohttp.
            limit: Количество изображений.
        
        Returns:
            Список словарей с информацией об изображениях.
        """
        url = f"{self._api_base_url}/images/search"
        params = {
            'limit': limit,
            'has_breeds': True,
            'api_key': self._api_key
        }
        
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data
    
    async def _download_image(
        self,
        session: aiohttp.ClientSession,
        image_url: str,
        image_index: int
    ) -> Tuple[int, bytes]:
        """
        Асинхронно скачивает изображение.
        
        Args:
            session: Асинхронная сессия aiohttp.
            image_url: URL изображения.
            image_index: Порядковый номер изображения.
        
        Returns:
            Кортеж (индекс, байты изображения).
        """
        print(f"Downloading image {image_index} started")
        
        async with session.get(image_url) as response:
            response.raise_for_status()
            image_data = await response.read()
        
        print(f"Downloading image {image_index} finished")
        return image_index, image_data
    
    async def _save_image(
        self,
        image: np.ndarray,
        filepath: str,
        image_index: int,
        image_type: str
    ) -> None:
        """
        Асинхронно сохраняет изображение в файл.
        
        Args:
            image: Массив numpy с изображением.
            filepath: Путь для сохранения.
            image_index: Порядковый номер изображения.
            image_type: Тип изображения (original, custom, library).
        """
        print(f"Saving image {image_index} ({image_type}) started")
        
        # Кодируем изображение в PNG
        _, buffer = cv2.imencode('.png', image)
        
        # Асинхронно записываем в файл
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(buffer.tobytes())
        
        print(f"Saving image {image_index} ({image_type}) finished: {filepath}")
    
    async def run(self, limit: int = 1) -> None:
        """
        Основной асинхронный метод для обработки изображений.
        
        Args:
            limit: Количество изображений для обработки.
        """
        start_time = time.perf_counter()
        
        print(f"=== Начало асинхронной обработки {limit} изображений ===")
        print(f"API: {self._api_type}")
        print(f"Директория сохранения: {self._output_dir}")
        print(f"Количество процессов для обработки: {self._max_workers}\n")
        
        await self._ensure_output_dir()
        
        async with aiohttp.ClientSession() as session:
            # Шаг 1: Получаем список URL изображений
            print("Получение списка URL изображений...")
            image_data_list = await self._fetch_image_urls(session, limit)
            
            # Присваиваем порядковые номера
            indexed_images = []
            for idx, item in enumerate(image_data_list, start=1):
                image_url = item.get('url')
                breed_info = item.get('breeds', [{}])[0]
                breed_name = breed_info.get('name', 'unknown')
                indexed_images.append({
                    'index': idx,
                    'url': image_url,
                    'breed': breed_name
                })
            
            print(f"Получено {len(indexed_images)} URL изображений\n")
            
            # Шаг 2: Асинхронно скачиваем все изображения
            print("Начало асинхронной загрузки изображений...")
            download_tasks = [
                self._download_image(session, img['url'], img['index'])
                for img in indexed_images
            ]
            downloaded_images = await asyncio.gather(*download_tasks)
            print("Все изображения загружены\n")
            
            # Создаём словарь для быстрого доступа
            images_dict = {idx: data for idx, data in downloaded_images}
            
            # Шаг 3: Сохраняем оригинальные изображения асинхронно
            print("Сохранение оригинальных изображений...")
            save_original_tasks = []
            for img_info in indexed_images:
                idx = img_info['index']
                breed = img_info['breed']
                image_data = images_dict[idx]
                
                # Декодируем для сохранения оригинала
                image_array = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                safe_breed = self._sanitize_filename(breed)
                filepath = os.path.join(
                    self._output_dir,
                    f"{idx}_{safe_breed}_original.png"
                )
                save_original_tasks.append(
                    self._save_image(image, filepath, idx, 'original')
                )
            
            await asyncio.gather(*save_original_tasks)
            print("Все оригинальные изображения сохранены\n")
            
            # Шаг 4: Параллельная обработка изображений (свёртка)
            print("Начало параллельной обработки изображений...")
            loop = asyncio.get_event_loop()
            
            with ProcessPoolExecutor(max_workers=self._max_workers) as executor:
                # Создаём задачи для параллельной обработки
                process_tasks = []
                for img_info in indexed_images:
                    idx = img_info['index']
                    breed = img_info['breed']
                    url = img_info['url']
                    image_data = images_dict[idx]
                    
                    task = loop.run_in_executor(
                        executor,
                        apply_convolution_worker,
                        image_data,
                        idx,
                        breed,
                        url
                    )
                    process_tasks.append(task)
                
                # Ждём завершения всех обработок
                processed_results = await asyncio.gather(*process_tasks)
            
            print("Все изображения обработаны\n")
            
            # Шаг 5: Асинхронно сохраняем обработанные изображения
            print("Сохранение обработанных изображений...")
            save_processed_tasks = []
            
            for idx, custom_edges, library_edges, breed in processed_results:
                safe_breed = self._sanitize_filename(breed)
                
                # Сохраняем custom edges
                custom_path = os.path.join(
                    self._output_dir,
                    f"{idx}_{safe_breed}_custom.png"
                )
                save_processed_tasks.append(
                    self._save_image(custom_edges, custom_path, idx, 'custom')
                )
                
                # Сохраняем library edges
                library_path = os.path.join(
                    self._output_dir,
                    f"{idx}_{safe_breed}_library.png"
                )
                save_processed_tasks.append(
                    self._save_image(library_edges, library_path, idx, 'library')
                )
            
            await asyncio.gather(*save_processed_tasks)
            print("Все обработанные изображения сохранены\n")
        
        elapsed_time = time.perf_counter() - start_time
        
        print(f"=== Обработка завершена ===")
        print(f"Результаты сохранены в: {self._output_dir}")
        print(f"Общее время выполнения: {elapsed_time:.4f} секунд")
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Очищает имя файла от недопустимых символов.
        
        Args:
            filename: Исходное имя файла.
        
        Returns:
            Безопасное имя файла.
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = filename.strip()
        if not filename:
            filename = 'unknown'
        return filename
