"""
Модуль image_processing.py

Реализация интерфейса IImageProcessing с использованием библиотеки OpenCV.

Содержит класс ImageProcessing, предоставляющий методы для обработки изображений:
- свёртка изображения с ядром
- преобразование RGB-изображения в оттенки серого
- гамма-коррекция
- обнаружение границ (оператор Кэнни)
- обнаружение углов (алгоритм Харриса)
- обнаружение окружностей
"""
import cv2
import interfaces
import numpy as np
from lab2.utils import timing_decorator


class ImageProcessing(interfaces.IImageProcessing):
    """
    Реализация интерфейса IImageProcessing с использованием библиотеки OpenCV.

    Предоставляет методы для обработки изображений, включая свёртку, преобразование
    в оттенки серого, гамма-коррекцию, а также обнаружение границ, углов и окружностей.
    """

    @timing_decorator
    def _convolution(self, image: np.ndarray, kernel: np.ndarray):
        """
        Выполняет свёртку изображения с заданным ядром.

        Args:
            image (np.ndarray): Входное изображение (может быть цветным или чёрно-белым).
            kernel (np.ndarray): Ядро свёртки (матрица).

        Returns:
            image (result_image)
        """
        # Извлекаем размеры изображения и ядра
        image_height, image_width = image.shape[:2]
        kernel_height, kernel_width = kernel.shape
        # Вычисляем паддинги по высоте и ширине, чтобы результат совпадал по размеру
        pad_height = kernel_height // 2
        pad_width = kernel_width // 2
        # Делаем отражённое/нулевое дополнение краёв изображения под свёртку
        if len(image.shape) == 3:
            padded_image = np.pad(
                image,
                ((pad_height, pad_height), (pad_width, pad_width), (0, 0)),
                mode='constant',
            )
        else:
            padded_image = np.pad(
                image,
                ((pad_height, pad_height), (pad_width, pad_width)),
                mode='constant',
            )
        # Подготавливаем выходной массив с плавающей точкой для аккумулирования суммы
        output = np.zeros_like(image, dtype=np.float32)
        # Проходим по каждому пикселю и применяем ядро свёртки
        for i in range(image_height):
            for j in range(image_width):
                if len(image.shape) == 3:
                    for channel in range(3):
                        region = padded_image[
                            i:i + kernel_height,
                            j:j + kernel_width,
                            channel
                        ]
                        output[i, j, channel] = np.sum(region * kernel)
                else:
                    region = padded_image[
                        i:i + kernel_height,
                        j:j + kernel_width
                    ]
                    output[i, j] = np.sum(region * kernel)
        # Обрезаем значения в допустимый диапазон [0, 255] и приводим к uint8
        output = np.clip(output, 0, 255).astype(np.uint8)
        return output

    @timing_decorator
    def _rgb_to_grayscale(self, image: np.ndarray):
        # Линейная комбинация каналов RGB в соответствии с яркостной моделью
        grayscale = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.float32)
        return grayscale

    @timing_decorator
    def _gamma_correction(self, image: np.ndarray, gamma: float = 1.0):
        """
        Применяет гамма-коррекцию к изображению.

        Args:
            image (np.ndarray): Входное изображение.
            gamma (float): Коэффициент гамма-коррекции (>0).

        Returns:
            image (corrected_image)
        """
        # Нормализация в диапазон [0,1]
        normalized_image = image.astype(np.float32) / 255.0
        # Применение степени gamma
        corrected_image = np.power(normalized_image, gamma)
        # Обратное масштабирование в [0,255] и приведение типа
        result = (corrected_image * 255).astype(np.uint8)
        return result

    @timing_decorator
    def sobel_operator(self, image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Применяет оператор Собеля для вычисления градиентов.

        Args:
            image (np.ndarray): Входное изображение.

        Returns:
            tuple: (gradient_x, gradient_y)
        """
        # Ядро Собеля по X
        sobel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]])
        # Ядро Собеля по Y
        sobel_y = np.array([[-1, -2, -1],
                            [0, 0, 0],
                            [1, 2, 1]])
        # Применяем свёртку для получения градиентов по X и Y
        gradient_x = self._convolution(image, sobel_x)
        gradient_y = self._convolution(image, sobel_y)
        return gradient_x, gradient_y

    @timing_decorator
    def simple_blur(self, img: np.ndarray) -> np.ndarray:
        # Простое усредняющее ядро 3x3
        blur_kernel = np.array(
            [
                [1 / 9, 1 / 9, 1 / 9],
                [1 / 9, 1 / 9, 1 / 9],
                [1 / 9, 1 / 9, 1 / 9],
            ]
        )
        # Свёртка с усредняющим ядром
        result = self._convolution(img, blur_kernel)
        return result

    @timing_decorator
    def edge_detection(self, image: np.ndarray):
        """
        Выполняет обнаружение границ на изображении.

        Args:
            image (np.ndarray): Входное изображение (RGB).

        Returns:
            image (edges_image)
        """
        # Преобразование в оттенки серого
        gray = self._rgb_to_grayscale(image)
        # Вычисление градиентов по осям с помощью оператора Собеля
        gradient_x, gradient_y = self.sobel_operator(gray)
        # Подсчёт магнитуды градиента
        gradient_magnitude = np.sqrt(
            gradient_x.astype(np.float32) ** 2
            + gradient_y.astype(np.float32) ** 2
        )
        # Нормализация магнитуды к диапазону [0,255]
        gradient_magnitude = (
            gradient_magnitude / gradient_magnitude.max() * 255
        ).astype(np.uint8)
        # Пороговая обработка для выделения границ
        edge_value = 50
        edges = np.where(gradient_magnitude > edge_value, 255, 0).astype(np.uint8)
        return edges

    @timing_decorator
    def corner_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Выполняет обнаружение углов на изображении по Харрису.

        Этапы: градиенты по X и Y (Собель), бокс-суммирование, отклик
        R = det(M) - k*(trace(M)**2), немаксимальное подавление и порог.

        Args:
            image (np.ndarray): Входное изображение (RGB).

        Returns:
            np.ndarray: Изображение с выделенными углами (белые точки).
        """
        # В оттенки серого
        gray = self._rgb_to_grayscale(image)
        # Градиенты по X и Y
        Ix, Iy = self.sobel_operator(gray)
        Ix = Ix.astype(np.float32)
        Iy = Iy.astype(np.float32)
        # Квадраты и произведение градиентов
        Ixx = Ix * Ix
        Iyy = Iy * Iy
        Ixy = Ix * Iy
        # Усреднение
        box_kernel = np.ones((3, 3), dtype=np.float32) / 9
        Sxx = self._convolution(Ixx, box_kernel)
        Syy = self._convolution(Iyy, box_kernel)
        Sxy = self._convolution(Ixy, box_kernel)
        # Расчёт отклика Харриса
        k = 0.04
        det_M = Sxx * Syy - Sxy * Sxy
        trace_M = Sxx + Syy
        R = det_M - k * (trace_M ** 2)
        # Нормализация и порог
        R_norm = (R - R.min()) / (R.max() - R.min())
        threshold = 0.2
        corners = np.zeros_like(R_norm, dtype=np.uint8)
        corners[R_norm > threshold] = 255
        # Немаксимальное подавление
        nms_size = 3
        half = nms_size // 2
        result = np.zeros_like(corners)
        for y in range(half, corners.shape[0] - half):
            for x in range(half, corners.shape[1] - half):
                local_region = R_norm[y - half:y + half + 1, x - half:x + half + 1]
                if R_norm[y, x] == local_region.max() and R_norm[y, x] > threshold:
                    result[y, x] = 255
        # Визуализация на копии исходного изображения
        result_image = image.copy()
        ys, xs = np.where(result > 0)
        for (x, y) in zip(xs, ys):
            if len(result_image.shape) == 3:
                result_image[y, x] = (0, 0, 255)
            else:
                result_image[y, x] = 255

        return result_image
        

    @timing_decorator
    def circle_detection(self, image: np.ndarray):
        """
        Выполняет обнаружение окружностей на изображении с помощью преобразования Хафа.
        """
        # Уменьшение размера изображения для ускорения
        scale_factor = 0.3
        h, w = image.shape[:2]
        new_h, new_w = int(h * scale_factor), int(w * scale_factor)
        # Простое уменьшение изображения
        if len(image.shape) == 3:
            small_image = np.zeros((new_h, new_w, 3), dtype=image.dtype)
            for i in range(new_h):
                for j in range(new_w):
                    orig_i = min(int(i / scale_factor), h - 1)
                    orig_j = min(int(j / scale_factor), w - 1)
                    small_image[i, j] = image[orig_i, orig_j]
        else:
            small_image = np.zeros((new_h, new_w), dtype=image.dtype)
            for i in range(new_h):
                for j in range(new_w):
                    orig_i = min(int(i / scale_factor), h - 1)
                    orig_j = min(int(j / scale_factor), w - 1)
                    small_image[i, j] = image[orig_i, orig_j]
        # Обнаружение границ
        edges = self.edge_detection(small_image)
        edges_binary = (edges > 100).astype(np.uint8) * 255
        # Параметры преобразования Хафа
        height, width = edges_binary.shape
        min_radius = 20
        max_radius = min(height, width) // 6
        radius_step = 2
        print(f"Диапазон радиусов: {min_radius}-{max_radius} с шагом {radius_step}")
        # Сэмплирование набора граничных точек для ускорения
        edge_points = np.argwhere(edges_binary > 0)
        sampling_rate = 2
        sampled_edge_points = edge_points[::sampling_rate]
        print(
            f"Всего точек границ: {len(edge_points)}, "
            f"после сэмплирования: {len(sampled_edge_points)}"
        )
        # Создаем аккумулятор
        accumulator = np.zeros(
            (height, width, (max_radius - min_radius) // radius_step + 1),
            dtype=np.uint16,
        )
        # Голосование: для каждой точки и набора радиусов инкрементируем возможные центры
        print("Начало оптимизированного голосования...")
        for i, (y, x) in enumerate(sampled_edge_points):
            if i % 500 == 0:
                print(f"Обработано {i}/{len(sampled_edge_points)} точек...")
            # Перебор углов для аппроксимации окружности
            angle_step = 6
            for angle in range(0, 360, angle_step):
                theta = np.radians(angle)
                for r_idx, radius in enumerate(
                    range(min_radius, max_radius + 1, radius_step)
                ):
                    a = int(x - radius * np.cos(theta))
                    b = int(y - radius * np.sin(theta))
                    if 0 <= a < width and 0 <= b < height:
                        accumulator[b, a, r_idx] += 1
        print("Поиск окружностей...")
        # Порог на аккумуляторе для выделения сильных кандидатов
        threshold = 0.6 * np.max(accumulator)
        circles = []
        for r_idx, radius in enumerate(
            range(min_radius, max_radius + 1, radius_step)
        ):
            acc_layer = accumulator[:, :, r_idx]
            strong_candidates = np.argwhere(acc_layer > threshold)
            for y, x in strong_candidates:
                # Устраняем дубликаты близко расположенных центров/радиусов
                is_duplicate = False
                for existing_x, existing_y, existing_r in circles:
                    distance = np.sqrt((x - existing_x) ** 2 + (y - existing_y) ** 2)
                    if distance < 38 and abs(radius - existing_r) < 25:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    circles.append((x, y, radius))
                    if len(circles) >= 20:
                        break
            if len(circles) >= 20:
                break
        print(f"Найдено окружностей: {len(circles)}")
        # Масштабируем координаты обратно к исходному изображению и рисуем окружности
        result = image.copy()
        for (x, y, radius) in circles:
            x_orig = int(x / scale_factor)
            y_orig = int(y / scale_factor)
            radius_orig = int(radius / scale_factor)
            self.draw_circle(result, x_orig, y_orig, radius_orig, (0, 255, 0), 2)
            cv2.circle(result, (x_orig, y_orig), 3, (0, 0, 255), -1)
        return result

    @timing_decorator
    def draw_circle(self, image: np.ndarray, center_x: int, center_y: int,
                    radius: int, color: tuple, thickness: int = 2) -> None:
        """
        Рисует окружность на изображении с помощью алгоритма Брезенхэма.

        Args:
            image (np.ndarray): Изображение для рисования.
            center_x (int): X-координата центра.
            center_y (int): Y-координата центра.
            radius (int): Радиус окружности.
            color (tuple): Цвет в формате BGR.
            thickness (int): Толщина линии.
        """
        # Инициализация параметров алгоритма Брезенхэма
        x = 0
        y = radius
        d = 3 - 2 * radius

        def draw_points(xc, yc, x, y):
            # Формируем список симметричных точек окружности
            points = []
            points.extend([
                (xc + x, yc + y), (xc - x, yc + y),
                (xc + x, yc - y), (xc - x, yc - y),
                (xc + y, yc + x), (xc - y, yc + x),
                (xc + y, yc - x), (xc - y, yc - x)
            ])
            if thickness > 1:
                # Утолщаем линию за счёт соседних пикселей
                for dx in range(-thickness // 2, thickness // 2 + 1):
                    for dy in range(-thickness // 2, thickness // 2 + 1):
                        if dx != 0 or dy != 0:
                            for px, py in points.copy():
                                points.append((px + dx, py + dy))
            # Отрисовываем валидные точки на изображении
            for px, py in points:
                if 0 <= px < image.shape[1] and 0 <= py < image.shape[0]:
                    image[py, px] = color
        # Основной цикл построения окружности
        while y >= x:
            draw_points(center_x, center_y, x, y)
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            draw_points(center_x, center_y, x, y)
