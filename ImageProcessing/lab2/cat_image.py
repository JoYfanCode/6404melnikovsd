"""
Модуль cat_image.py

Абстрактный класс CatImage и его конкретные реализации для работы
с изображениями животных.
"""

import abc
import numpy as np
from typing import Optional


class CatImage(abc.ABC):
    """
    Абстрактный базовый класс для работы с изображениями животных.

    Инкапсулирует скачанное изображение и его метаданные, а также
    методы обработки изображения.
    """

    def __init__(
        self,
        image: np.ndarray,
        image_url: str,
        breed: str
    ) -> None:
        """
        Инициализация изображения животного.

        Args:
            image: Массив numpy с изображением.
            image_url: URL исходного изображения.
            breed: Порода животного.
        """
        self._image = image
        self._image_url = image_url
        self._breed = breed

    @property
    def image(self) -> np.ndarray:
        """Возвращает изображение как numpy массив."""
        return self._image

    @property
    def image_url(self) -> str:
        """Возвращает URL изображения."""
        return self._image_url

    @property
    def breed(self) -> str:
        """Возвращает породу животного."""
        return self._breed

    @abc.abstractmethod
    def detect_edges_custom(self) -> np.ndarray:
        """
        Выделение границ пользовательским методом.

        Returns:
            Изображение с выделенными границами.
        """
        pass

    @abc.abstractmethod
    def detect_edges_library(self) -> np.ndarray:
        """
        Выделение границ библиотечным методом (OpenCV).

        Returns:
            Изображение с выделенными границами.
        """
        pass

    def __add__(self, other: 'CatImage') -> 'CatImage':
        """
        Перегрузка оператора сложения изображений.

        Args:
            other: Другое изображение для сложения.

        Returns:
            Новое изображение - результат сложения.
        """
        if not isinstance(other, CatImage):
            raise TypeError("Можно складывать только CatImage")
        if self._image.shape != other._image.shape:
            raise ValueError("Изображения должны иметь одинаковый размер")

        result_image = np.clip(
            self._image.astype(np.float32) + other._image.astype(np.float32),
            0, 255
        ).astype(np.uint8)

        return self.__class__(
            result_image,
            f"{self._image_url} + {other._image_url}",
            f"{self._breed}_mixed"
        )

    def __sub__(self, other: 'CatImage') -> 'CatImage':
        """
        Перегрузка оператора вычитания изображений.

        Args:
            other: Другое изображение для вычитания.

        Returns:
            Новое изображение - результат вычитания.
        """
        if not isinstance(other, CatImage):
            raise TypeError("Можно вычитать только CatImage")
        if self._image.shape != other._image.shape:
            raise ValueError("Изображения должны иметь одинаковый размер")

        result_image = np.clip(
            self._image.astype(np.float32) - other._image.astype(np.float32),
            0, 255
        ).astype(np.uint8)

        return self.__class__(
            result_image,
            f"{self._image_url} - {other._image_url}",
            f"{self._breed}_diff"
        )

    def __str__(self) -> str:
        """
        Преобразование в строку.

        Returns:
            Строковое представление изображения.
        """
        shape = self._image.shape
        return (
            f"CatImage(breed={self._breed}, "
            f"shape={shape}, url={self._image_url[:50]}...)"
        )

    def __repr__(self) -> str:
        """Возвращает строковое представление для отладки."""
        return self.__str__()


class ColorCatImage(CatImage):
    """
    Конкретная реализация CatImage для цветных изображений.
    """

    def detect_edges_custom(self) -> np.ndarray:
        """
        Выделение границ пользовательским методом (оператор Собеля).

        Returns:
            Изображение с выделенными границами в градациях серого.
        """
        from implementation.image_processing import ImageProcessing

        processor = ImageProcessing()

        # Преобразуем в grayscale
        gray = processor._rgb_to_grayscale(self._image)

        # Применяем оператор Собеля
        gradient_x, gradient_y = processor.sobel_operator(gray)

        # Вычисляем магнитуду градиента
        gradient_magnitude = np.sqrt(
            gradient_x.astype(np.float32) ** 2 +
            gradient_y.astype(np.float32) ** 2
        )

        # Нормализация
        if gradient_magnitude.max() > 0:
            gradient_magnitude = (
                gradient_magnitude / gradient_magnitude.max() * 255
            ).astype(np.uint8)
        else:
            gradient_magnitude = gradient_magnitude.astype(np.uint8)

        # Пороговая обработка
        edges = np.where(gradient_magnitude > 50, 255, 0).astype(np.uint8)

        # Конвертируем обратно в RGB для единообразия
        edges_rgb = np.stack([edges, edges, edges], axis=-1)

        return edges_rgb

    def detect_edges_library(self) -> np.ndarray:
        """
        Выделение границ библиотечным методом (Canny из OpenCV).

        Returns:
            Изображение с выделенными границами.
        """
        import cv2

        gray = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        return edges_rgb


class GrayscaleCatImage(CatImage):
    """
    Конкретная реализация CatImage для чёрно-белых изображений.
    """

    def detect_edges_custom(self) -> np.ndarray:
        """
        Выделение границ пользовательским методом (оператор Собеля).

        Returns:
            Изображение с выделенными границами.
        """
        from implementation.image_processing import ImageProcessing

        processor = ImageProcessing()

        # Применяем оператор Собеля
        gradient_x, gradient_y = processor.sobel_operator(self._image)

        # Вычисляем магнитуду градиента
        gradient_magnitude = np.sqrt(
            gradient_x.astype(np.float32) ** 2 +
            gradient_y.astype(np.float32) ** 2
        )

        # Нормализация
        if gradient_magnitude.max() > 0:
            gradient_magnitude = (
                gradient_magnitude / gradient_magnitude.max() * 255
            ).astype(np.uint8)
        else:
            gradient_magnitude = gradient_magnitude.astype(np.uint8)

        # Пороговая обработка
        edges = np.where(gradient_magnitude > 50, 255, 0).astype(np.uint8)

        return edges

    def detect_edges_library(self) -> np.ndarray:
        """
        Выделение границ библиотечным методом (Canny из OpenCV).

        Returns:
            Изображение с выделенными границами.
        """
        import cv2

        edges = cv2.Canny(self._image, 50, 150)

        return edges

