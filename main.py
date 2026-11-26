"""Запуск программы FdF из командной строки."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from fdf.errors import FdfError
from fdf.parser import parse_map


def main(argv: Sequence[str] | None = None) -> int:
    """Прочитать карту и показать её размер."""
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Использование: python main.py <файл.fdf>", file=sys.stderr)
        return 2

    path = Path(arguments[0])
    try:
        height_map = parse_map(path)
    except OSError as error:
        print(f"Не удалось прочитать «{path}»: {error.strerror or error}", file=sys.stderr)
        return 1
    except FdfError as error:
        print(f"Ошибка в карте «{path}»: {error}", file=sys.stderr)
        return 1

    print(f"{height_map.width} × {height_map.height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
