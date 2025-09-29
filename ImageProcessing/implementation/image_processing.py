"""
Реализация интерфейса IImageProcessing с использованием библиотеки OpenCV.

Предоставляет методы для обработки изображений: свёртка, преобразование в
оттенки серого, гамма-коррекция, а также обнаружение границ, углов и
окружностей.

Методы:
- _convolution(image, kernel): свёртка изображения с ядром
- _rgb_to_grayscale(image): преобразование RGB в оттенки серого
- _gamma_correction(image, gamma): гамма-коррекция
- edge_detection(image): обнаружение границ (Собель + порог)
- corner_detection(image): обнаружение углов (Харрис)
- circle_detection(image): обнаружение окружностей (параметрическое Хафа)
"""
import interfaces

import numpy as np


class ImageProcessing(interfaces.IImageProcessing):
    """Реализация абстрактного интерфейса обработки изображений."""
    def _convolution(
        self: "ImageProcessing",
        image: np.ndarray,
        kernel: np.ndarray,
    ) -> np.ndarray:
        """
        Выполняет свёртку изображения с заданным ядром.

        Реализована собственная свёртка с нулевым дополнением (zero padding).

        Args:
            image (np.ndarray): Входное изображение (цветное или чёрно-белое).
            kernel (np.ndarray): Ядро свёртки (матрица).

        Returns:
            np.ndarray: Изображение после применения свёртки.
        """

        if image.ndim == 2:
            image_channels = 1
            image_expanded = image[..., None]
        else:
            image_channels = image.shape[2]
            image_expanded = image

        kh, kw = kernel.shape
        pad_h = kh // 2
        pad_w = kw // 2
        kernel_flipped = np.flipud(np.fliplr(kernel))

        padded = np.pad(
            image_expanded,
            ((pad_h, pad_h), (pad_w, pad_w), (0, 0)),
            mode="constant",
        )

        out = np.zeros_like(image_expanded, dtype=np.float64)
        for row_index in range(out.shape[0]):
            row_slice = slice(row_index, row_index + kh)
            for col_index in range(out.shape[1]):
                col_slice = slice(col_index, col_index + kw)
                window = padded[row_slice, col_slice, :]
                out[row_index, col_index, :] = np.tensordot(
                    window,
                    kernel_flipped,
                    axes=([0, 1], [0, 1]),
                )

        if np.issubdtype(image.dtype, np.integer):
            out = np.clip(out, 0, 255)
            out = out.astype(image.dtype)
        else:
            out = out.astype(image.dtype)

        return out[..., 0] if image_channels == 1 else out

    def _rgb_to_grayscale(
        self: "ImageProcessing",
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Преобразует RGB-изображение в оттенки серого.

        Реализовано вручную как взвешенная сумма каналов. Если изображение
        прочитано через OpenCV (BGR), используются коэффициенты в порядке
        B,G,R.

        Args:
            image (np.ndarray): Входное RGB-изображение.

        Returns:
            np.ndarray: Одноканальное изображение в оттенках серого.
        """

        if image.ndim == 2:
            return image

        blue_channel = image[..., 0].astype(np.float32)
        green_channel = image[..., 1].astype(np.float32)
        red_channel = image[..., 2].astype(np.float32)
        gray = (
            0.114 * blue_channel
            + 0.587 * green_channel
            + 0.299 * red_channel
        )
        gray = np.clip(gray, 0, 255)
        return gray.astype(image.dtype)

    def _gamma_correction(
        self: "ImageProcessing",
        image: np.ndarray,
        gamma: float,
    ) -> np.ndarray:
        """
        Применяет гамма-коррекцию к изображению.

        Реализовано вручную через степенное преобразование значений пикселей.

        Args:
            image (np.ndarray): Входное изображение.
            gamma (float): Коэффициент гамма-коррекции (>0).

        Returns:
            np.ndarray: Изображение после гамма-коррекции.
        """
        if gamma <= 0:
            raise ValueError("gamma должен быть > 0")

        image_float = image.astype(np.float32) / 255.0
        corrected = np.power(image_float, gamma)
        corrected = np.clip(corrected * 255.0, 0, 255)
        return corrected.astype(image.dtype)

    def edge_detection(
        self: "ImageProcessing",
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Выполняет обнаружение границ на изображении.

        Детектирование границ с помощью операторов Собеля по X и Y и порог по
        величине градиента.

        Args:
            image (np.ndarray): Входное изображение (RGB).

        Returns:
            np.ndarray: Одноканальное изображение с выделенными границами.
        """
        gray = self._rgb_to_grayscale(image).astype(np.float32)

        sobel_x = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1],
        ], dtype=np.float32)

        sobel_y = np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1],
        ], dtype=np.float32)

        grad_x = self._convolution(gray, sobel_x).astype(np.float32)
        grad_y = self._convolution(gray, sobel_y).astype(np.float32)
        mag = np.hypot(grad_x, grad_y)
        mag = (mag / (mag.max() + 1e-8)) * 255.0

        thresh = 0.3 * 255.0
        edges = (mag >= thresh).astype(np.uint8) * 255
        return edges

    def corner_detection(
        self: "ImageProcessing",
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Выполняет обнаружение углов на изображении по Харрису.

        Этапы: градиенты по X и Y (Собель), бокс-суммирование, отклик
        R = det(M) - k*(trace(M)**2), немаксимальное подавление и порог.

        Args:
            image (np.ndarray): Входное изображение (RGB).

        Returns:
            np.ndarray: Изображение с выделенными углами (белые точки).
        """

        gray = self._rgb_to_grayscale(image).astype(np.float32)
        sobel_x = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1],
        ], dtype=np.float32)

        sobel_y = np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1],
        ], dtype=np.float32)

        grad_x = self._convolution(gray, sobel_x).astype(np.float32)
        grad_y = self._convolution(gray, sobel_y).astype(np.float32)

        ixx = grad_x * grad_x
        iyy = grad_y * grad_y
        ixy = grad_x * grad_y

        box3 = np.ones((3, 3), dtype=np.float32) / 9.0
        sxx = self._convolution(ixx, box3)
        syy = self._convolution(iyy, box3)
        sxy = self._convolution(ixy, box3)

        harris_k = 0.04
        det = sxx * syy - sxy * sxy
        trace = sxx + syy
        r_response = det - harris_k * (trace ** 2)

        r_norm = r_response - r_response.min()
        if r_norm.max() > 0:
            r_norm = r_norm / r_norm.max()

        # Порог, чтобы не заливать всё изображение
        thresh = 0.1

        # Подавление немаксимумов в окне 3x3
        height, width = r_norm.shape
        nms = np.zeros_like(r_norm, dtype=bool)
        for row_index in range(1, height - 1):
            for col_index in range(1, width - 1):
                center = r_norm[row_index, col_index]
                if center < thresh:
                    continue

                r0 = row_index - 1
                r1 = row_index + 2
                c0 = col_index - 1
                c1 = col_index + 2
                local = r_norm[r0:r1, c0:c1]
                if (
                    center == local.max()
                    and np.count_nonzero(local == center) == 1
                ):
                    nms[row_index, col_index] = True

        img_height, img_width = gray.shape
        out = np.zeros((img_height, img_width, 3), dtype=image.dtype)

        out[nms] = [255, 255, 255]
        return out

    def circle_detection(
        self: "ImageProcessing",
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Выполняет обнаружение окружностей (параметрическое Хафа).

        Args:
            image (np.ndarray): Входное изображение (RGB).

        Returns:
            np.ndarray: Изображение с выделенными окружностями.
        """

        # 1) Подготовка: градации серого и границы
        gray = self._rgb_to_grayscale(image).astype(np.float32)
        edges = self.edge_detection(image)
        edge_points = np.argwhere(edges > 0)

        height, width = gray.shape

        # 2) Параметры Хафа
        min_radius = max(10, min(height, width) // 20)
        max_radius = max(min(height, width) // 4, min_radius + 1)
        radii = np.arange(min_radius, max_radius, 2, dtype=int)

        angles_rad = np.deg2rad(np.arange(0, 360, 5, dtype=float))
        cos_theta = np.cos(angles_rad)
        sin_theta = np.sin(angles_rad)

        # 3) Аккумулятор: (h, w, num_radii)
        acc = np.zeros((height, width, len(radii)), dtype=np.uint16)

        for (row_index, col_index) in edge_points:
            for radius_index, radius in enumerate(radii):
                ys = (row_index - (radius * sin_theta)).round().astype(int)
                xs = (col_index - (radius * cos_theta)).round().astype(int)
                valid = (
                    (ys >= 0)
                    & (ys < height)
                    & (xs >= 0)
                    & (xs < width)
                )
                ys = ys[valid]
                xs = xs[valid]
                acc[ys, xs, radius_index] += 1

        # 4) Поиск пиков в аккумляторе по каждому радиусу с NMS
        circles = []  # (row, col, radius, votes)
        for radius_index, radius in enumerate(radii):
            layer = acc[:, :, radius_index]
            if layer.max() == 0:
                continue

            threshold = max(10, int(0.6 * layer.max()))
            # NMS 7x7
            for row_index in range(3, height - 3):
                for col_index in range(3, width - 3):
                    votes = layer[row_index, col_index]
                    if votes < threshold:
                        continue

                    r0 = row_index - 3
                    r1 = row_index + 4
                    c0 = col_index - 3
                    c1 = col_index + 4
                    window = layer[r0:r1, c0:c1]
                    if (
                        votes == window.max()
                        and np.count_nonzero(window == votes) == 1
                    ):
                        circles.append(
                            (row_index, col_index, int(radius), int(votes)),
                        )

        # Отсортируем по голосам и ограничим количество
        circles.sort(key=lambda tpl: tpl[3], reverse=True)
        keep = []

        def far_enough(y_center: int, x_center: int, radius: int) -> bool:
            """Проверяет отдалённость от уже выбранных окружностей.

            Args:
                y_center (int): Координата Y центра новой окружности.
                x_center (int): Координата X центра новой окружности.
                radius (int): Радиус новой окружности.

            Returns:
                bool: True, если окружность достаточно далеко от выбранных.
            """
            for (y2, x2, _r2, _) in keep:
                if (
                    (y_center - y2) ** 2
                    + (x_center - x2) ** 2
                    < (0.8 * radius) ** 2
                ):
                    return False

            return True

        for circle in circles:
            if far_enough(circle[0], circle[1], circle[2]):
                keep.append(circle)

            if len(keep) >= 10:
                break

        # 5) Отрисовка: окружность
        result = np.zeros((height, width, 3), dtype=image.dtype)
        for (y_center, x_center, radius, _) in keep:
            for angle_deg in range(0, 360, 2):
                angle_rad = np.deg2rad(angle_deg)
                y_pix = int(round(y_center + radius * np.sin(angle_rad)))
                x_pix = int(round(x_center + radius * np.cos(angle_rad)))
                if 0 <= y_pix < height and 0 <= x_pix < width:
                    result[y_pix, x_pix] = [255, 255, 255]

            if 0 <= y_center < height and 0 <= x_center < width:
                result[y_center, x_center] = [255, 255, 255]

        return result
