"""Точки и прямоугольная сетка карты высот."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int
    z: int
    color: str | None = None


class Map:
    """Сетка с обходом по строкам и доступом к точкам через map[x, y]."""

    def __init__(self, rows: Sequence[Sequence[Point]]) -> None:
        self.rows = tuple(tuple(row) for row in rows)
        if not self.rows or not self.rows[0]:
            raise ValueError("Карта должна содержать хотя бы одну точку")

        self.width = len(self.rows[0])
        self.height = len(self.rows)
        if any(len(row) != self.width for row in self.rows):
            raise ValueError("Все строки карты должны иметь одинаковую длину")

    def __len__(self) -> int:
        return self.width * self.height

    def __iter__(self) -> Iterator[Point]:
        for row in self.rows:
            yield from row

    def __getitem__(self, position: tuple[int, int]) -> Point:
        x, y = position
        return self.rows[y][x]

    def neighbors(self, point: Point | int, y: int | None = None) -> Iterator[Point]:
        """Вернуть существующих соседей справа и снизу в этом порядке."""
        if isinstance(point, Point):
            x, y = point.x, point.y
        elif y is not None:
            x = point
        else:
            raise TypeError("Укажите точку или обе координаты")

        if x + 1 < self.width:
            yield self[x + 1, y]
        if y + 1 < self.height:
            yield self[x, y + 1]
