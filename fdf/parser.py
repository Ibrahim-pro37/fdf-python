"""Чтение карт формата .fdf с диагностикой по строкам и колонкам."""

import re
from pathlib import Path

from .errors import FdfError as FdfError
from .errors import MapFormatError as MapFormatError
from .model import Map, Point

_INTEGER = re.compile(r"[+-]?[0-9]+")
_COLOR = re.compile(r"0[xX][0-9A-Fa-f]{1,6}")


def parse_value(value: str, line: int = 1, column: int = 1) -> tuple[int, str | None]:
    """Разобрать высоту и необязательный цвет одной точки."""
    height, separator, color = value.partition(",")
    if not _INTEGER.fullmatch(height):
        raise MapFormatError(line, column, f"{height!r} — не целое число")

    try:
        z = int(height)
    except ValueError as error:
        raise MapFormatError(
            line, column, "высота содержит слишком много цифр"
        ) from error

    if not separator:
        return z, None
    if not _COLOR.fullmatch(color):
        raise MapFormatError(line, column, f"{color!r} — некорректный цвет")
    return z, f"#{int(color, 16):06X}"


def parse_map(path: str | Path) -> Map:
    """Прочитать карту. Ошибки доступа к файлу передаются вызывающему коду."""
    rows: list[list[Point]] = []
    first_blank: int | None = None
    # Некорректные байты попадут в проверку токенов с номером строки и колонки.
    with Path(path).open(encoding="utf-8-sig", errors="surrogateescape") as source:
        for line, text in enumerate(source, start=1):
            values = text.split()
            if not values:
                if first_blank is None:
                    first_blank = line
                continue
            if first_blank is not None:
                raise MapFormatError(first_blank, 1, "пустая строка внутри карты")
            if rows:
                expected_width = len(rows[0])
                if len(values) != expected_width:
                    raise MapFormatError(
                        line,
                        min(len(values), expected_width) + 1,
                        f"ожидалось {expected_width} значений, найдено {len(values)}",
                    )

            row: list[Point] = []
            for x, value in enumerate(values):
                z, color = parse_value(value, line, x + 1)
                row.append(Point(x, line - 1, z, color))
            rows.append(row)

    if not rows:
        raise MapFormatError(1, 1, "карта пуста")
    return Map(rows)
