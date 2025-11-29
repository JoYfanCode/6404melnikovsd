"""
Модуль утилит для лабораторной работы №2.
"""

import functools
import time
from typing import Callable, Any


def timing_decorator(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения метода.

    Args:
        func: Функция или метод для измерения времени.

    Returns:
        Обёрнутая функция с логированием времени выполнения.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_time = time.perf_counter() - start_time
        class_name = args[0].__class__.__name__ if args else 'Unknown'
        print(
            f"[{class_name}.{func.__name__}] "
            f"Выполнено за {elapsed_time:.4f} секунд"
        )
        return result
    return wrapper

