"""Проекция точек на экран и интерполяция цветов."""

import math
from dataclasses import dataclass

from .model import Map, Point

_HEIGHT_PALETTE = ("#528DF6", "#55C9AA", "#FFE065", "#FF795D")


@dataclass
class Camera:
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    z_scale: float = 1.0
    angle: float = 30.0
    top_view: bool = False

    def _on_plane(self, point: Point) -> tuple[float, float]:
        if self.top_view:
            return point.x, point.y

        slope = math.radians(self.angle)
        x = (point.x - point.y) * math.cos(slope)
        y = (point.x + point.y) * math.sin(slope) - point.z * self.z_scale
        return x, y

    def project(self, point: Point) -> tuple[float, float]:
        x, y = self._on_plane(point)
        return x * self.scale + self.offset_x, y * self.scale + self.offset_y

    def fit(self, height_map: Map, width: int, height: int) -> None:
        """Вписать проекцию карты в окно, оставив поля с каждой стороны."""
        points = iter(height_map)
        left, top = self._on_plane(next(points))
        right, bottom = left, top
        for point in points:
            x, y = self._on_plane(point)
            left, right = min(left, x), max(right, x)
            top, bottom = min(top, y), max(bottom, y)

        fit_x = width / (right - left) if right > left else math.inf
        fit_y = height / (bottom - top) if bottom > top else math.inf
        fit_scale = min(fit_x, fit_y)
        self.scale = 0.9 * fit_scale if math.isfinite(fit_scale) else 1.0

        center_x = left / 2 + right / 2
        center_y = top / 2 + bottom / 2
        self.offset_x = width / 2 - center_x * self.scale
        self.offset_y = height / 2 - center_y * self.scale


def lerp_color(start: str, end: str, t: float) -> str:
    """Смешать два цвета #RRGGBB независимо по каждому каналу."""
    t = max(0.0, min(t, 1.0))
    channels: list[str] = []
    for index in (1, 3, 5):
        a = int(start[index : index + 2], 16)
        b = int(end[index : index + 2], 16)
        channels.append(f"{round((1 - t) * a + t * b):02X}")
    return "#" + "".join(channels)


def height_color(z: int, z_min: int, z_max: int) -> str:
    """Выбрать цвет из палитры по относительной высоте точки."""
    if z_min == z_max:
        return _HEIGHT_PALETTE[0]

    last_index = len(_HEIGHT_PALETTE) - 1
    ratio = (z - z_min) / (z_max - z_min)
    position = max(0.0, min(ratio, 1.0)) * last_index
    index = min(int(position), last_index - 1)
    return lerp_color(
        _HEIGHT_PALETTE[index], _HEIGHT_PALETTE[index + 1], position - index
    )
