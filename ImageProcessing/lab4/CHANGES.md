# Изменения в лабораторной работе №4 по сравнению с lab2

## Основные улучшения

### 1. Асинхронная загрузка изображений (aiohttp)

**Lab2 (синхронная):**
```python
def _download_image(self, url: str) -> np.ndarray:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    image_array = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image
```

**Lab4 (асинхронная):**
```python
async def _download_image(
    self,
    session: aiohttp.ClientSession,
    image_url: str,
    image_index: int
) -> Tuple[int, bytes]:
    print(f"Downloading image {image_index} started")
    async with session.get(image_url) as response:
        response.raise_for_status()
        image_data = await response.read()
    print(f"Downloading image {image_index} finished")
    return image_index, image_data
```

**Преимущества:**
- Все изображения загружаются одновременно
- Не блокируется выполнение программы во время ожидания ответа от сервера
- Значительное ускорение при загрузке нескольких изображений

### 2. Асинхронное сохранение файлов (aiofiles)

**Lab2 (синхронная):**
```python
cv2.imwrite(filepath, image)
```

**Lab4 (асинхронная):**
```python
async def _save_image(
    self,
    image: np.ndarray,
    filepath: str,
    image_index: int,
    image_type: str
) -> None:
    print(f"Saving image {image_index} ({image_type}) started")
    _, buffer = cv2.imencode('.png', image)
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(buffer.tobytes())
    print(f"Saving image {image_index} ({image_type}) finished")
```

**Преимущества:**
- Неблокирующая запись файлов
- Возможность сохранять несколько файлов одновременно
- Улучшенная производительность при работе с медленными дисками

### 3. Параллельная обработка изображений (ProcessPoolExecutor)

**Lab2 (последовательная):**
```python
for idx, cat_image in enumerate(cat_images, start=1):
    custom_edges = cat_image.detect_edges_custom()
    library_edges = cat_image.detect_edges_library()
    # Сохранение...
```

**Lab4 (параллельная):**
```python
def apply_convolution_worker(
    image_data: bytes,
    image_index: int,
    breed: str,
    image_url: str
) -> Tuple[int, np.ndarray, np.ndarray, str]:
    pid = os.getpid()
    print(f"Convolution for image {image_index} started (PID {pid})")
    # Обработка изображения...
    print(f"Convolution for image {image_index} finished (PID {pid})")
    return image_index, custom_edges, library_edges, breed

# В основном коде:
with ProcessPoolExecutor(max_workers=self._max_workers) as executor:
    process_tasks = []
    for img_info in indexed_images:
        task = loop.run_in_executor(
            executor,
            apply_convolution_worker,
            image_data, idx, breed, url
        )
        process_tasks.append(task)
    processed_results = await asyncio.gather(*process_tasks)
```

**Преимущества:**
- Использование всех ядер процессора
- Параллельная обработка нескольких изображений одновременно
- Значительное ускорение при обработке большого количества изображений

### 4. Сохранение порядковых номеров

**Lab4:**
```python
# Присваиваем порядковые номера в самом начале
indexed_images = []
for idx, item in enumerate(image_data_list, start=1):
    indexed_images.append({
        'index': idx,  # Номер фиксируется и не меняется
        'url': image_url,
        'breed': breed_name
    })
```

**Преимущества:**
- Порядковый номер определяется при получении списка URL
- Номер не меняется на протяжении всей обработки
- Легко отследить какое изображение обрабатывается

### 5. Детальное логирование

**Lab4:**
```python
print(f"Downloading image {image_index} started")
print(f"Downloading image {image_index} finished")
print(f"Convolution for image {image_index} started (PID {pid})")
print(f"Convolution for image {image_index} finished (PID {pid})")
print(f"Saving image {image_index} ({image_type}) started")
print(f"Saving image {image_index} ({image_type}) finished")
```

**Преимущества:**
- Видно, что обработка действительно идёт асинхронно/параллельно
- Можно отследить PID процесса для каждой обработки
- Легко понять на каком этапе находится каждое изображение

## Дополнительное задание: Генераторный пайплайн

Реализован асинхронный генераторный пайплайн, где каждый этап - отдельный генератор:

```python
async def fetch_metadata_generator(self, limit: int) -> AsyncGenerator[Dict, None]:
    # Получение метаданных
    yield metadata

async def download_generator(self, metadata_gen) -> AsyncGenerator[Dict, None]:
    async for metadata in metadata_gen:
        # Загрузка изображения
        yield metadata_with_image

async def process_generator(self, download_gen) -> AsyncGenerator[Dict, None]:
    async for metadata in download_gen:
        # Обработка изображения
        yield metadata_with_processed

async def save_generator(self, process_gen) -> AsyncGenerator[Dict, None]:
    async for metadata in process_gen:
        # Сохранение результатов
        yield metadata
```

**Преимущества:**
- Этапы не блокируют друг друга
- Обработка начинается сразу после загрузки первого изображения
- Более эффективное использование ресурсов
- Меньшее потребление памяти (обрабатываем по одному изображению)

## Ожидаемое ускорение

При обработке 5 изображений:
- **Lab2 (синхронная):** ~20-30 секунд
- **Lab4 (асинхронная):** ~8-12 секунд
- **Ускорение:** 2-3x

При обработке 10 изображений:
- **Lab2 (синхронная):** ~40-60 секунд
- **Lab4 (асинхронная):** ~15-20 секунд
- **Ускорение:** 2.5-3.5x

Ускорение зависит от:
- Скорости интернет-соединения (для загрузки)
- Количества ядер процессора (для обработки)
- Скорости диска (для сохранения)

## Структура проекта

```
lab4/
├── __init__.py                      # Инициализация модуля
├── async_cat_image_processor.py     # Основной класс (основное задание)
├── async_pipeline_processor.py      # Генераторный пайплайн (доп. задание)
├── main_lab4.py                     # Точка входа (основное задание)
├── main_lab4_pipeline.py            # Точка входа (доп. задание)
├── compare_performance.py           # Сравнение с lab2
├── requirements.txt                 # Зависимости
├── README.md                        # Документация
├── LAB4_BASH.md                     # Команды для запуска
└── CHANGES.md                       # Этот файл
```

## Использованные технологии

- **aiohttp** - асинхронные HTTP-запросы
- **aiofiles** - асинхронная работа с файлами
- **asyncio** - асинхронное программирование
- **ProcessPoolExecutor** - параллельная обработка в отдельных процессах
- **multiprocessing** - определение количества ядер CPU
- **AsyncGenerator** - асинхронные генераторы для пайплайна
