import pytest

from fdf.model import Map, Point


@pytest.fixture
def grid() -> Map:
    return Map([[Point(x, y, x + y) for x in range(3)] for y in range(2)])


def test_length_and_iteration(grid: Map) -> None:
    assert (grid.width, grid.height, len(grid)) == (3, 2, 6)
    assert [(point.x, point.y) for point in grid] == [
        (0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)
    ]


def test_corner_neighbors(grid: Map) -> None:
    assert tuple(grid.neighbors(grid[0, 0])) == (grid[1, 0], grid[0, 1])
    assert tuple(grid.neighbors(grid[2, 1])) == ()


def test_neighbors_form_each_edge_once(grid: Map) -> None:
    edges = [
        frozenset(((point.x, point.y), (neighbor.x, neighbor.y)))
        for point in grid
        for neighbor in grid.neighbors(point)
    ]
    expected_edge_count = (grid.width - 1) * grid.height + (grid.height - 1) * grid.width

    assert len(edges) == len(set(edges)) == expected_edge_count
