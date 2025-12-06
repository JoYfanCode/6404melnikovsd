### Базовый запуск

```bash
python main_lab2.py
```

### Обработка нескольких изображений

```bash
python main_lab2.py --limit 5
```

### Указание своей директории для сохранения

```bash
python main_lab2.py --output-dir my_images --limit 2
```

### Все параметры

```bash
python main_lab2.py --limit 3 --output-dir lab2_images --api-key YOUR_KEY
```

### Операции

```bash
python add_two_images.py lab2_images/1_Bengal_original.png lab2_images/1_Bengal_custom.png lab2_images/my_result.png
```

## Параметры командной строки

- `--limit` - Количество изображений для обработки (по умолчанию: 1)
- `--api-type` - Тип API: `cat` или `dog` (по умолчанию: `cat`)
- `--api-key` - API ключ (по умолчанию берётся из `.env` файла)
- `--output-dir` - Директория для сохранения результатов (по умолчанию: `lab2_images`)