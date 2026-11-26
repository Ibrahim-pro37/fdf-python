import pytest

from fdf.model import Point
from fdf.projection import Camera, height_color, lerp_color


def test_top_view_ignores_height() -> None:
    camera = Camera(top_view=True)

    assert camera.project(Point(2, 3, -9)) == pytest.approx((2, 3))
    assert camera.project(Point(2, 3, 12)) == pytest.approx((2, 3))


def test_rotation_and_height_scale() -> None:
    camera = Camera(angle=0, z_scale=2)

    assert camera.project(Point(2, 1, 3)) == pytest.approx((1, -6))


def test_color_interpolates_each_channel() -> None:
    start, end = "#004000", "#F0A060"

    assert lerp_color(start, end, 0) == start
    assert lerp_color(start, end, 0.5) == "#787030"
    assert lerp_color(start, end, 1) == end


def test_height_color_handles_flat_map_and_a_range() -> None:
    flat = height_color(4, 4, 4)
    low = height_color(-3, -3, 5)
    middle = height_color(1, -3, 5)
    high = height_color(5, -3, 5)

    for color in (flat, low, middle, high):
        assert color.startswith("#") and len(color) == 7
        assert color[1:] == f"{int(color[1:], 16):06X}"
    assert len({low, middle, high}) == 3
