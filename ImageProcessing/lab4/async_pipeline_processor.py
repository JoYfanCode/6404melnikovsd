"""
Модуль async_pipeline_processor.py

Асинхронный генераторный пайплайн для обработки изображений.

Дополнительное задание: каждому этапу обработки соответствует отдельный генератор.
"""

import os
import asyncio
import aiohttp
import aiofiles
import numpy as np
import cv2
from typing import AsyncGenerator, Dict, Tuple
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor
import time
import multiprocessing as mp

from lab2.cat_image import ColorCatImage, GrayscaleCatImage

load_dotenv()


def apply_convolution_worker(
    image_data: bytes,
    image_index: int,
    breed: str,
    image_url: str
) -> Tuple[int, np.ndarray, np.ndarray, np.ndarray, str]:
    """
    Функция для параллельной обработки изображения.
    
    Args:
        image_data: Байты изображения.
        image_index: Порядковый номер изображения.
        breed: Порода животного.
        image_url: URL изображения.
    
    Returns:
        Кортеж (индекс, original, custom_edges, library_edges, breed).
    """
    pid = os.getpid()
    print(f"[Pipeline] Convolution for image {image_index} started (PID {pid})")
    
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
    
    print(f"[Pipeline] Convolution for image {image_index} finished (PID {pid})")
    
    return image_index, image, custom_edges, library_edges, breed


class AsyncPipelineProcessor:
    """
    Асинхронный генераторный пайплайн для обработки изображений.
    
    Каждый этап (скачивание, обработка, сохранение) реализован как отдельный
    асинхронный генератор, что позволяет этапам работать параллельно.
    """
    
    def __init__(
        self,
        api_key: str = None,
        api_type: str = 'cat',
        output_dir: str = 'lab4_pipeline_images',
        max_workers: int = None
    ) -> None:
        """
        Инициализация пайплайн-процессора.
        
        Args:
            api_key: API ключ для доступа к API.
            api_type: Тип API (только 'cat').
            output_dir: Директория для сохранения результатов.
            max_workers: Максимальное количество процессов для обработки.
        """
        self._api_key = api_key or os.getenv('API_KEY')
        if not self._api_key:
            raise ValueError("API_KEY не найден.")
        
        self._api_type = api_type.lower()
        if self._api_type == 'cat':
            self._api_base_url = 'https://api.thecatapi.com/v1'
        else:
            raise ValueError("api_type должен быть 'cat'")
        
        self._output_dir = output_dir
        self._max_workers = max_workers or mp.cpu_count()
        self._executor = None
    
    async def _ensure_output_dir(self) -> None:
        """Создаёт директорию для сохранения."""
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
            print(f"Создана директория: {self._output_dir}")
    
    async def fetch_metadata_generator(
        self,
        limit: int
    ) -> AsyncGenerator[Dict, None]:
        """
        Генератор этапа 1: получение метаданных изображений из API.
        
        Args:
            limit: Количество изображений.
        
        Yields:
            Словарь с метаданными изображения (index, url, breed).
        """
        print("[Pipeline Stage 1] Fetching metadata started")
        
        url = f"{self._api_base_url}/images/search"
        params = {
            'limit': limit,
            'has_breeds': True,
            'api_key': self._api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                for idx, item in enumerate(data, start=1):
                    image_url = item.get('url')
                    breed_info = item.get('breeds', [{}])[0]
                    breed_name = breed_info.get('name', 'unknown')
                    
                    metadata = {
                        'index': idx,
                        'url': image_url,
                        'breed': breed_name
                    }
                    
                    print(f"[Pipeline Stage 1] Metadata for image {idx} ready")
                    yield metadata
        
        print("[Pipeline Stage 1] Fetching metadata finished")
    
    async def download_generator(
        self,
        metadata_gen: AsyncGenerator[Dict, None]
    ) -> AsyncGenerator[Dict, None]:
        """
        Генератор этапа 2: асинхронная загрузка изображений.
        
        Args:
            metadata_gen: Генератор метаданных.
        
        Yields:
            Словарь с метаданными и загруженными данными изображения.
        """
        print("[Pipeline Stage 2] Downloading started")
        
        async with aiohttp.ClientSession() as session:
            async for metadata in metadata_gen:
                idx = metadata['index']
                url = metadata['url']
                
                print(f"[Pipeline Stage 2] Downloading image {idx} started")
                
                async with session.get(url) as response:
                    response.raise_for_status()
                    image_data = await response.read()
                
                print(f"[Pipeline Stage 2] Downloading image {idx} finished")
                
                metadata['image_data'] = image_data
                yield metadata
        
        print("[Pipeline Stage 2] Downloading finished")
    
    async def process_generator(
        self,
        download_gen: AsyncGenerator[Dict, None]
    ) -> AsyncGenerator[Dict, None]:
        """
        Генератор этапа 3: параллельная обработка изображений (свёртка).
        
        Args:
            download_gen: Генератор загруженных изображений.
        
        Yields:
            Словарь с метаданными и обработанными изображениями.
        """
        print("[Pipeline Stage 3] Processing started")
        
        loop = asyncio.get_event_loop()
        
        if self._executor is None:
            self._executor = ProcessPoolExecutor(max_workers=self._max_workers)
        
        async for metadata in download_gen:
            idx = metadata['index']
            breed = metadata['breed']
            url = metadata['url']
            image_data = metadata['image_data']
            
            # Запускаем обработку в отдельном процессе
            result = await loop.run_in_executor(
                self._executor,
                apply_convolution_worker,
                image_data,
                idx,
                breed,
                url
            )
            
            idx, original, custom_edges, library_edges, breed = result
            
            metadata['original'] = original
            metadata['custom_edges'] = custom_edges
            metadata['library_edges'] = library_edges
            
            # Удаляем image_data для экономии памяти
            del metadata['image_data']
            
            yield metadata
        
        print("[Pipeline Stage 3] Processing finished")
    
    async def save_generator(
        self,
        process_gen: AsyncGenerator[Dict, None]
    ) -> AsyncGenerator[Dict, None]:
        """
        Генератор этапа 4: асинхронное сохранение изображений.
        
        Args:
            process_gen: Генератор обработанных изображений.
        
        Yields:
            Словарь с метаданными (для возможного дальнейшего использования).
        """
        print("[Pipeline Stage 4] Saving started")
        
        async for metadata in process_gen:
            idx = metadata['index']
            breed = metadata['breed']
            original = metadata['original']
            custom_edges = metadata['custom_edges']
            library_edges = metadata['library_edges']
            
            safe_breed = self._sanitize_filename(breed)
            
            # Сохраняем все три изображения параллельно
            save_tasks = []
            
            # Оригинал
            original_path = os.path.join(
                self._output_dir,
                f"{idx}_{safe_breed}_original.png"
            )
            save_tasks.append(
                self._save_image(original, original_path, idx, 'original')
            )
            
            # Custom edges
            custom_path = os.path.join(
                self._output_dir,
                f"{idx}_{safe_breed}_custom.png"
            )
            save_tasks.append(
                self._save_image(custom_edges, custom_path, idx, 'custom')
            )
            
            # Library edges
            library_path = os.path.join(
                self._output_dir,
                f"{idx}_{safe_breed}_library.png"
            )
            save_tasks.append(
                self._save_image(library_edges, library_path, idx, 'library')
            )
            
            await asyncio.gather(*save_tasks)
            
            yield metadata
        
        print("[Pipeline Stage 4] Saving finished")
    
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
            image_type: Тип изображения.
        """
        print(f"[Pipeline Stage 4] Saving image {image_index} ({image_type}) started")
        
        # Кодируем изображение в PNG
        _, buffer = cv2.imencode('.png', image)
        
        # Асинхронно записываем в файл
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(buffer.tobytes())
        
        print(f"[Pipeline Stage 4] Saving image {image_index} ({image_type}) finished")
    
    async def run(self, limit: int = 1) -> None:
        """
        Запускает генераторный пайплайн обработки.
        
        Args:
            limit: Количество изображений для обработки.
        """
        start_time = time.perf_counter()
        
        print(f"=== Начало генераторного пайплайна ({limit} изображений) ===")
        print(f"API: {self._api_type}")
        print(f"Директория сохранения: {self._output_dir}")
        print(f"Количество процессов: {self._max_workers}\n")
        
        await self._ensure_output_dir()
        
        try:
            # Создаём пайплайн из генераторов
            metadata_gen = self.fetch_metadata_generator(limit)
            download_gen = self.download_generator(metadata_gen)
            process_gen = self.process_generator(download_gen)
            save_gen = self.save_generator(process_gen)
            
            # Запускаем пайплайн
            count = 0
            async for _ in save_gen:
                count += 1
            
            print(f"\nОбработано изображений: {count}")
            
        finally:
            # Закрываем executor
            if self._executor is not None:
                self._executor.shutdown(wait=True)
        
        elapsed_time = time.perf_counter() - start_time
        
        print(f"\n=== Пайплайн завершён ===")
        print(f"Результаты сохранены в: {self._output_dir}")
        print(f"Общее время выполнения: {elapsed_time:.4f} секунд")
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Очищает имя файла от недопустимых символов."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = filename.strip()
        if not filename:
            filename = 'unknown'
        return filename
