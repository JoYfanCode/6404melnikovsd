# Лабораторная работа №2

## Описание

Программа для обработки изображений животных через API (TheCatAPI или TheDogAPI) с выделением контуров пользовательским и библиотечным методами.

## Требования

- Python 3.11+
- API ключ от https://thecatapi.com/ или https://thedogapi.com/

## Установка

1. Установите зависимости:
```bash
pipenv install
# или
pip install -r requirements.txt
```

2. Создайте файл `.env` в корне проекта:
```env
API_KEY=your_api_key_here
```

Получите API ключ:
- https://thecatapi.com/ (регистрация бесплатная)
- https://thedogapi.com/ (регистрация бесплатная)

## Использование

### Базовый запуск (1 изображение)

```bash
python main_lab2.py
```

### Обработка нескольких изображений

```bash
python main_lab2.py --limit 5
```

### Использование Dog API

```bash
python main_lab2.py --api-type dog --limit 3
```

### Указание своей директории для сохранения

```bash
python main_lab2.py --output-dir my_images --limit 2
```

### Все параметры

```bash
python main_lab2.py --limit 3 --api-type cat --output-dir lab2_images --api-key YOUR_KEY
```

## Параметры командной строки

- `--limit` - Количество изображений для обработки (по умолчанию: 1)
- `--api-type` - Тип API: `cat` или `dog` (по умолчанию: `cat`)
- `--api-key` - API ключ (по умолчанию берётся из `.env` файла)
- `--output-dir` - Директория для сохранения результатов (по умолчанию: `lab2_images`)

## Структура проекта

```
lab2/
├── __init__.py              # Инициализация модуля
├── cat_image.py             # Абстрактный класс CatImage и реализации
├── cat_image_processor.py   # Класс CatImageProcessor
└── utils.py                 # Утилиты (декораторы)

main_lab2.py                 # Точка входа
.env                         # API ключ (не в git)
lab2_images/                 # Директория с результатами
```

## Структура классов

### CatImage (абстрактный)

- Абстрактный базовый класс для работы с изображениями
- Перегрузка операторов `+`, `-`, `__str__`
- Методы: `detect_contours_custom()`, `detect_contours_library()`

### ColorCatImage

- Реализация для цветных изображений
- Наследуется от `CatImage`

### GrayscaleCatImage

- Реализация для чёрно-белых изображений
- Наследуется от `CatImage`

### CatImageProcessor

- Работа с API (загрузка изображений)
- Обработка и сохранение результатов
- Измерение времени выполнения методов (через декоратор)

## Формат сохраняемых файлов

Для каждого изображения создаются 3 файла:

1. `{номер}_{порода}_original.png` - исходное изображение
2. `{номер}_{порода}_custom.png` - контуры пользовательским методом
3. `{номер}_{порода}_library.png` - контуры библиотечным методом (Canny)

Пример:
- `1_munchkin_original.png`
- `1_munchkin_custom.png`
- `1_munchkin_library.png`

## Особенности реализации

1. **Абстрактный класс**: `CatImage` является абстрактным базовым классом
2. **Наследование**: Реализации для цветных и Ч/Б изображений
3. **Перегрузка операторов**: `+` и `-` для операций с изображениями
4. **Декораторы**: `@timing_decorator` для измерения времени выполнения
5. **Инкапсуляция**: Защищённые атрибуты с `@property`
6. **Типизация**: Полная аннотация типов

## Пример вывода

```
=== Начало обработки 2 изображений ===
API: cat
Директория сохранения: lab2_images

[CatImageProcessor.fetch_images] Загрузка 2 изображений из cat API...
Загружено изображение: munchkin
Загружено изображение: persian
[CatImageProcessor.fetch_images] Выполнено за 1.2345 секунд

Обработка изображения 1/2: munchkin
Сохранено исходное изображение: lab2_images/1_munchkin_original.png
[ColorCatImage.detect_contours_custom] Выполнено за 0.1234 секунд
Сохранено изображение (custom): lab2_images/1_munchkin_custom.png
[ColorCatImage.detect_contours_library] Выполнено за 0.0567 секунд
Сохранено изображение (library): lab2_images/1_munchkin_library.png

=== Обработка завершена ===
Результаты сохранены в: lab2_images
```

