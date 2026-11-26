from pathlib import Path

import pytest

from fdf.errors import FdfError, MapFormatError
from fdf.model import Point
from fdf.parser import parse_map, parse_value

MAPS = Path(__file__).resolve().parents[1] / "maps"


def test_parse_elem() -> None:
    height_map = parse_map(MAPS / "elem.fdf")

    assert (height_map.width, height_map.height) == (5, 5)
    assert height_map[2, 2] == Point(2, 2, 5)
    assert [(point.x, point.y) for point in height_map] == [
        (x, y) for y in range(5) for x in range(5)
    ]


def test_parse_partial_colors() -> None:
    height_map = parse_map(MAPS / "peak.fdf")

    assert height_map[2, 2].color == "#FF0000"
    assert height_map[0, 0].color == "#0000FF"
    assert height_map[1, 1].color is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("7", (7, None)),
        ("-3", (-3, None)),
        ("2,0xFF8800", (2, "#FF8800")),
        ("1,0xff", (1, "#0000FF")),
        ("-2,0xaBc", (-2, "#000ABC")),
    ],
)
def test_parse_value(value: str, expected: tuple[int, str | None]) -> None:
    assert parse_value(value, 1, 1) == expected


@pytest.mark.parametrize(
    ("filename", "position"),
    [
        ("empty.fdf", "строка 1, колонка 1"),
        ("invalid_value.fdf", "строка 2, колонка 3"),
        ("ragged.fdf", "строка 2, колонка 3"),
        ("invalid_color.fdf", "строка 2, колонка 2"),
        ("blank_row.fdf", "строка 2, колонка 1"),
    ],
)
def test_invalid_map_has_error_location(filename: str, position: str) -> None:
    with pytest.raises(MapFormatError, match=position) as error:
        parse_map(MAPS / "bad" / filename)

    assert isinstance(error.value, FdfError)


@pytest.mark.parametrize("value", ["2,", "2,ff", "2,0x1234567", "2,0xff,0xff", "1_000"])
def test_reject_malformed_value(value: str) -> None:
    with pytest.raises(MapFormatError, match="строка 3, колонка 2"):
        parse_value(value, 3, 2)


def test_whitespace_and_trailing_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "spaces.fdf"
    path.write_text("  1   -2  \n3 4\n \n\n", encoding="utf-8")

    height_map = parse_map(path)

    assert (height_map.width, height_map.height) == (2, 2)
    assert [point.z for point in height_map] == [1, -2, 3, 4]


def test_missing_file_raises_os_error(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        parse_map(tmp_path / "missing.fdf")
