"""Тесты геометрии: направления и игровое поле."""

import pytest

from snake_game.geometry import Board, Cell, Direction


@pytest.mark.parametrize('direction', list(Direction))
def test_opposite_is_an_involution(direction: Direction) -> None:
    assert direction.opposite is not direction
    assert direction.opposite.opposite is direction


@pytest.mark.parametrize(('direction', 'expected'), [
    (Direction.UP, Direction.DOWN),
    (Direction.DOWN, Direction.UP),
    (Direction.LEFT, Direction.RIGHT),
    (Direction.RIGHT, Direction.LEFT),
])
def test_opposite_direction(direction: Direction,
                            expected: Direction) -> None:
    assert direction.opposite is expected


@pytest.mark.parametrize(('cell', 'direction', 'expected'), [
    ((2, 2), Direction.RIGHT, (3, 2)),
    ((2, 2), Direction.LEFT, (1, 2)),
    ((2, 2), Direction.UP, (2, 1)),
    ((2, 2), Direction.DOWN, (2, 3)),
    ((4, 0), Direction.RIGHT, (0, 0)),
    ((0, 0), Direction.LEFT, (4, 0)),
    ((0, 0), Direction.UP, (0, 3)),
    ((0, 3), Direction.DOWN, (0, 0)),
])
def test_step_wraps_around_edges(cell: Cell, direction: Direction,
                                 expected: Cell) -> None:
    assert Board(5, 4).step(cell, direction) == expected


@pytest.mark.parametrize(('first', 'second', 'expected'), [
    ((0, 0), (0, 0), 0),
    ((0, 0), (2, 1), 3),
    ((2, 1), (0, 0), 3),
    ((0, 0), (9, 0), 1),   # короче через край поля
    ((0, 0), (0, 9), 1),
    ((1, 1), (9, 9), 4),
    ((0, 0), (5, 5), 10),  # ровно половина поля по обеим осям
])
def test_distance_accounts_for_wrapping(first: Cell, second: Cell,
                                        expected: int) -> None:
    assert Board(10, 10).distance(first, second) == expected


def test_center_of_default_board() -> None:
    assert Board(32, 24).center == (16, 12)


def test_free_cells_excludes_occupied() -> None:
    assert Board(2, 2).free_cells([(0, 0), (1, 1)]) == [(1, 0), (0, 1)]


def test_free_cells_of_empty_board_is_every_cell() -> None:
    assert len(Board(4, 3).free_cells([])) == 12


def test_free_cells_ignores_duplicates_and_foreign_cells() -> None:
    cells = Board(2, 2).free_cells([(0, 0), (0, 0), (9, 9)])
    assert cells == [(1, 0), (0, 1), (1, 1)]


@pytest.mark.parametrize(('width', 'height'), [(1, 5), (5, 1), (0, 0)])
def test_too_small_board_is_rejected(width: int, height: int) -> None:
    with pytest.raises(ValueError):
        Board(width, height)
