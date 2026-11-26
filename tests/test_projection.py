from math import sqrt
from pathlib import Path

import pytest

from fdf.model import Map, Point
from fdf.parser import parse_map
from fdf.projection import Camera

MAPS = Path(__file__).resolve().parents[1] / "maps"


def test_isometric_projection() -> None:
    camera = Camera()

    assert camera.project(Point(0, 0, 0)) == pytest.approx((0, 0))
    assert camera.project(Point(1, 0, 0)) == pytest.approx((sqrt(3) / 2, 0.5))
    assert camera.project(Point(0, 1, 0)) == pytest.approx((-sqrt(3) / 2, 0.5))
    assert camera.project(Point(0, 0, 1))[1] < 0


@pytest.mark.parametrize(("width", "height"), [(800, 240), (240, 800)])
def test_fit_contains_and_centers_map(width: int, height: int) -> None:
    height_map = Map([[Point(x, y, x - 2 * y) for x in range(5)] for y in range(4)])
    camera = Camera()

    camera.fit(height_map, width, height)
    x_values, y_values = zip(*(camera.project(point) for point in height_map), strict=True)
    min_x, max_x, min_y, max_y = min(x_values), max(x_values), min(y_values), max(y_values)

    assert 0 <= min_x <= max_x <= width
    assert 0 <= min_y <= max_y <= height
    assert (min_x + max_x, min_y + max_y) == pytest.approx((width, height))
    assert max((max_x - min_x) / width, (max_y - min_y) / height) == pytest.approx(0.9)


def test_fit_centers_single_point() -> None:
    point = Point(0, 0, 9)
    camera = Camera()

    camera.fit(Map([[point]]), 300, 200)

    assert camera.project(point) == pytest.approx((150, 100))


def test_flat_map_projects_to_symmetric_rhombus() -> None:
    height_map = parse_map(MAPS / "flat.fdf")
    camera = Camera()
    camera.fit(height_map, 600, 400)

    left = camera.project(height_map[0, 4])
    right = camera.project(height_map[4, 0])
    top = camera.project(height_map[0, 0])
    bottom = camera.project(height_map[4, 4])

    assert (top[0], bottom[0]) == pytest.approx((300, 300))
    assert (left[1], right[1]) == pytest.approx((200, 200))
    assert left[0] + right[0] == pytest.approx(600)
    assert top[1] + bottom[1] == pytest.approx(400)
