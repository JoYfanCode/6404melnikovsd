# Быстрый старт - Лабораторная работа №4

## Шаг 1: Установка зависимостей

### Вариант 1: pip

```bash
pip install aiohttp aiofiles
```

### Вариант 2: из файла requirements.txt

```bash
pip install -r lab4/requirements.txt
```

### Вариант 3: pipenv (если используется)

```bash
pipenv install aiohttp aiofiles
```

## Шаг 2: Проверка API ключа

Убедитесь, что в файле `.env` есть ваш API ключ:

```
API_KEY=your_api_key_here
```

Получить API ключ можно на https://thecatapi.com/

## Шаг 3: Запуск

### Основное задание (5 изображений)

```bash
python lab4/main_lab4.py
```

### Дополнительное задание - генераторный пайплайн (5 изображений)

```bash
python lab4/main_lab4_pipeline.py
```

### Сравнение производительности с lab2

```bash
python lab4/compare_performance.py --limit 5
```

## Результаты

После выполнения программы:

- **Основное задание:** результаты в папке `lab4_images/`
- **Генераторный пайплайн:** результаты в папке `lab4_pipeline_images/`
- **Сравнение:** результаты в папках `lab2_images_test/` и `lab4_images_test/`

Каждое изображение сохраняется в трёх вариантах:
- `N_Breed_original.png` - оригинальное изображение
- `N_Breed_custom.png` - обработка пользовательским методом (Sobel)
- `N_Breed_library.png` - обработка библиотечным методом (Canny)

## Ожидаемый вывод

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
...

Начало параллельной обработки изображений...
Convolution for image 1 started (PID 12345)
Convolution for image 2 started (PID 12346)
...

=== Обработка завершена ===
Результаты сохранены в: lab4_images
Общее время выполнения: 8.1234 секунд
```

## Параметры запуска

```bash
# Обработать 10 изображений
python lab4/main_lab4.py --limit 10

# Указать количество процессов
python lab4/main_lab4.py --limit 5 --max-workers 4

# Указать свою директорию
python lab4/main_lab4.py --output-dir my_images --limit 3

# Все параметры вместе
python lab4/main_lab4.py --limit 10 --max-workers 4 --output-dir my_lab4
```

## Проверка работы

1. Убедитесь, что программа выводит сообщения о начале и завершении каждого этапа
2. Проверьте, что разные изображения обрабатываются с разными PID (это означает параллельную обработку)
3. Сравните время выполнения с lab2 - должно быть значительно быстрее

## Возможные проблемы

### ModuleNotFoundError: No module named 'aiohttp'

**Решение:** Установите зависимости (см. Шаг 1)

### API_KEY не найден

**Решение:** Создайте файл `.env` в корне проекта и добавьте туда ваш API ключ

### Ошибка при загрузке изображений

**Решение:** Проверьте интернет-соединение и правильность API ключа

## Дополнительная информация

- Полная документация: `lab4/README.md`
- Список изменений: `lab4/CHANGES.md`
- Команды для запуска: `lab4/LAB4_BASH.md`
