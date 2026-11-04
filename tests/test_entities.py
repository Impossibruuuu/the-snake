"""Тесты сущностей: змейка и яблоко."""

import random

import pytest

from snake_game.entities import Apple, Snake
from snake_game.geometry import Board, Direction

START = (5, 5)


@pytest.mark.parametrize('direction', list(Direction))
def test_reverse_direction_is_ignored(board: Board,
                                      direction: Direction) -> None:
    snake = Snake(START, direction)
    snake.steer(direction.opposite)
    snake.move(board)
    assert snake.head == board.step(START, direction)


@pytest.mark.parametrize(('direction', 'turn'), [
    (current, new)
    for current in Direction
    for new in Direction
    if new is not current.opposite
])
def test_allowed_turn_is_applied_on_next_move(
        board: Board, direction: Direction, turn: Direction) -> None:
    snake = Snake(START, direction)
    snake.steer(turn)
    snake.move(board)
    assert snake.head == board.step(START, turn)


def test_last_steer_before_move_wins(board: Board) -> None:
    snake = Snake(START, Direction.RIGHT)
    snake.steer(Direction.UP)
    snake.steer(Direction.DOWN)
    snake.move(board)
    assert snake.head == (5, 6)


def test_next_head_predicts_move_without_changing_snake(
        board: Board) -> None:
    snake = Snake(START, Direction.RIGHT)
    snake.steer(Direction.UP)
    assert snake.next_head(board) == (5, 4)
    assert snake.cells == (START,)
    snake.move(board)
    assert snake.head == (5, 4)


def test_move_without_growth_keeps_length(board: Board) -> None:
    snake = Snake(START, Direction.RIGHT)
    snake.move(board)
    assert len(snake) == 1
    assert snake.cells == ((6, 5),)


def test_grow_keeps_tail(board: Board) -> None:
    snake = Snake(START, Direction.RIGHT)
    snake.move(board, grow=True)
    assert snake.cells == ((6, 5), (5, 5))
    assert len(snake) == 2


def test_head_is_first_cell(board: Board) -> None:
    snake = Snake(START, Direction.RIGHT)
    snake.move(board, grow=True)
    snake.move(board, grow=True)
    assert snake.head == snake.cells[0] == (7, 5)


def test_straight_snake_does_not_hit_itself(board: Board) -> None:
    snake = Snake(START, Direction.RIGHT)
    for _ in range(4):
        snake.move(board, grow=True)
    assert not snake.hits_itself()


def test_hits_itself_when_head_enters_body(board: Board) -> None:
    snake = Snake(START, Direction.RIGHT)
    for _ in range(4):
        snake.move(board, grow=True)
    for turn in (Direction.DOWN, Direction.LEFT, Direction.UP):
        snake.steer(turn)
        snake.move(board)
    assert snake.hits_itself()


def test_head_may_take_the_cell_the_tail_just_left() -> None:
    board = Board(2, 2)
    snake = Snake((0, 0), Direction.RIGHT)
    snake.move(board, grow=True)
    snake.move(board, grow=True)
    snake.steer(Direction.DOWN)
    snake.move(board, grow=True)
    snake.steer(Direction.LEFT)
    snake.move(board)
    assert not snake.hits_itself()


@pytest.mark.parametrize('seed', range(25))
def test_apple_relocates_to_free_cell(board: Board, seed: int) -> None:
    occupied = [(x, y) for x in range(10) for y in range(9)]
    apple = Apple((0, 0))
    assert apple.relocate(board, occupied, random.Random(seed))
    assert apple.cell not in occupied
    assert apple.cell in board.free_cells([])


def test_apple_stays_put_when_board_is_full() -> None:
    board = Board(2, 2)
    apple = Apple((1, 1))
    full = board.free_cells([])
    assert not apple.relocate(board, full, random.Random(0))
    assert apple.cell == (1, 1)


def test_apple_relocation_is_reproducible_with_same_seed(
        board: Board) -> None:
    first, second = Apple((0, 0)), Apple((0, 0))
    first.relocate(board, [], random.Random(42))
    second.relocate(board, [], random.Random(42))
    assert first.cell == second.cell
