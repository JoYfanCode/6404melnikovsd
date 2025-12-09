# Команды для запуска лабораторной работы №4

## Установка зависимостей

```bash
pip install aiohttp aiofiles
```

## Основное задание

### Базовый запуск (5 изображений)

```bash
python lab4/main_lab4.py
```

### Обработка 10 изображений

```bash
python lab4/main_lab4.py --limit 10
```

### Указание количества процессов

```bash
python lab4/main_lab4.py --limit 5 --max-workers 4
```

### Указание своей директории

```bash
python lab4/main_lab4.py --output-dir my_lab4_images --limit 3
```

## Дополнительное задание (генераторный пайплайн)

### Базовый запуск

```bash
python lab4/main_lab4_pipeline.py
```

### С параметрами

```bash
python lab4/main_lab4_pipeline.py --limit 10 --max-workers 4
```

## Сравнение производительности

### Сравнение lab2 (синхронная) и lab4 (асинхронная)

```bash
python lab4/compare_performance.py --limit 5
```

### Сравнение с большим количеством изображений

```bash
python lab4/compare_performance.py --limit 10
```

## Примеры вывода

### Основная версия

```
=== Начало асинхронной обработки 5 изображений ===
API: cat
Директория сохранения: lab4_images
Количество процессов для обработки: 8

Получение списка URL изображений...
Получено 5 URL изображений

Начало асинхронной загрузки изображений...
Downloading image 1 started
Downloading image 2 started
Downloading image 3 started
Downloading image 4 started
Downloading image 5 started
Downloading image 2 finished
Downloading image 1 finished
Downloading image 4 finished
Downloading image 3 finished
Downloading image 5 finished
Все изображения загружены

Сохранение оригинальных изображений...
Saving image 1 (original) started
Saving image 2 (original) started
...

Начало параллельной обработки изображений...
Convolution for image 1 started (PID 12345)
Convolution for image 2 started (PID 12346)
Convolution for image 3 started (PID 12347)
Convolution for image 1 finished (PID 12345)
Convolution for image 2 finished (PID 12346)
...

=== Обработка завершена ===
Результаты сохранены в: lab4_images
Общее время выполнения: 8.1234 секунд
```

### Генераторный пайплайн

```
=== Начало генераторного пайплайна (5 изображений) ===
API: cat
Директория сохранения: lab4_pipeline_images
Количество процессов: 8

[Pipeline Stage 1] Fetching metadata started
[Pipeline Stage 2] Downloading started
[Pipeline Stage 3] Processing started
[Pipeline Stage 4] Saving started
[Pipeline Stage 1] Metadata for image 1 ready
[Pipeline Stage 2] Downloading image 1 started
[Pipeline Stage 1] Metadata for image 2 ready
[Pipeline Stage 2] Downloading image 1 finished
[Pipeline Stage 3] Convolution for image 1 started (PID 12345)
[Pipeline Stage 2] Downloading image 2 started
...

=== Пайплайн завершён ===
Результаты сохранены в: lab4_pipeline_images
Общее время выполнения: 7.8901 секунд
```

## Параметры командной строки

### main_lab4.py и main_lab4_pipeline.py

- `--limit` - Количество изображений (по умолчанию: 5)
- `--api-type` - Тип API: cat (по умолчанию: cat)
- `--api-key` - API ключ (по умолчанию из .env)
- `--output-dir` - Директория для результатов
- `--max-workers` - Количество процессов (по умолчанию: количество ядер CPU)

### compare_performance.py

- `--limit` - Количество изображений для сравнения (по умолчанию: 5)
