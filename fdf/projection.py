"""Изометрическая проекция точек карты на плоскость окна."""

import math
from dataclasses import dataclass

from .model import Map, Point

_COS_30 = math.cos(math.radians(30))
_SIN_30 = math.sin(math.radians(30))


@dataclass
class Camera:
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    z_scale: float = 1.0

    def _on_plane(self, point: Point) -> tuple[float, float]:
        x = (point.x - point.y) * _COS_30
        y = (point.x + point.y) * _SIN_30 - point.z * self.z_scale
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
