"""
Модуль lab2

Лабораторная работа №2: обработка изображений животных через API.
"""

from lab2.cat_image import CatImage, ColorCatImage, GrayscaleCatImage
from lab2.cat_image_processor import CatImageProcessor

__all__ = [
    'CatImage',
    'ColorCatImage',
    'GrayscaleCatImage',
    'CatImageProcessor',
]

