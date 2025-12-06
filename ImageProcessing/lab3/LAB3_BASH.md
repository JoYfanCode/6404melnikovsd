### Базовый запуск

```bash
python main_lab3.py --csv-file video_games.csv
```

### Указание размера чанка

```bash
python main_lab3.py --csv-file video_games.csv --chunksize 5000
```

### Изменение окна скользящего среднего

```bash
python main_lab3.py --csv-file video_games.csv --window 5
```

### Пропуск определённых задач

```bash
# Пропустить только задачу 4
python main_lab3.py --csv-file video_games.csv --skip-task 4

# Пропустить несколько задач
python main_lab3.py --csv-file video_games.csv --skip-task 2 4
```