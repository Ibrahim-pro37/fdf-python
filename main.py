"""Запуск программы FdF из командной строки."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from fdf.errors import FdfError
from fdf.parser import parse_map


def main(argv: Sequence[str] | None = None) -> int:
    """Прочитать карту и открыть окно просмотра."""
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

    try:
        from fdf.app import App

        App(height_map, path.name).run()
    except ImportError:
        print("Для просмотра карты нужен Python с поддержкой tkinter.", file=sys.stderr)
        return 1
    except FdfError as error:
        print(f"Ошибка FdF: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
