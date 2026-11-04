"""Тесты правил игры. Окно pygame для них не нужно."""

import random

import pytest

from snake_game.game import Command, Game, GameState
from snake_game.geometry import Board, Cell
from tests.helpers import crash_into_itself, feed_snake


@pytest.mark.parametrize('seed', range(20))
def test_new_game_apple_is_never_on_snake(board: Board, seed: int) -> None:
    new_game = Game(board, random.Random(seed))
    assert new_game.apple.cell not in new_game.snake.cells


def test_new_game_is_running_with_zero_score(game: Game) -> None:
    assert game.state is GameState.RUNNING
    assert game.score == 0
    assert len(game.snake) == 1
    assert game.snake.head == game.board.center


@pytest.mark.parametrize(('command', 'expected_head'), [
    (Command.TURN_UP, (5, 4)),
    (Command.TURN_DOWN, (5, 6)),
    (Command.TURN_LEFT, (6, 5)),   # разворот назад игнорируется
    (Command.TURN_RIGHT, (6, 5)),
])
def test_turn_commands_steer_the_snake(game: Game, command: Command,
                                       expected_head: Cell) -> None:
    game.handle(command)
    game.update()
    assert game.snake.head == expected_head


def test_snake_moves_every_update(game: Game) -> None:
    game.apple.cell = (0, 0)
    for step in range(1, 4):
        game.update()
        assert game.snake.head == (5 + step, 5)


def test_eating_apple_grows_snake_and_scores(game: Game) -> None:
    feed_snake(game, 1)
    assert game.score == 1
    assert len(game.snake) == 2
    assert game.apple.cell not in game.snake.cells


def test_score_counts_every_apple(game: Game) -> None:
    feed_snake(game, 3)
    assert game.score == 3
    assert len(game.snake) == 4


def test_missing_the_apple_changes_nothing(game: Game) -> None:
    game.apple.cell = (0, 0)
    game.update()
    assert game.score == 0
    assert game.apple.cell == (0, 0)


def test_self_collision_ends_game(game: Game) -> None:
    crash_into_itself(game)
    assert game.state is GameState.GAME_OVER


def test_game_over_freezes_the_world(game: Game) -> None:
    crash_into_itself(game)
    head, score = game.snake.head, game.score
    game.handle(Command.TURN_UP)
    game.update()
    assert game.snake.head == head
    assert game.score == score


def test_filling_the_whole_board_ends_game() -> None:
    tiny = Game(Board(2, 2), random.Random(0))
    for command in (Command.TURN_RIGHT, Command.TURN_DOWN,
                    Command.TURN_LEFT):
        tiny.handle(command)
        feed_snake(tiny, 1)
    assert tiny.score == 3
    assert tiny.state is GameState.GAME_OVER


def test_pause_freezes_the_world(game: Game) -> None:
    game.handle(Command.TOGGLE_PAUSE)
    head = game.snake.head
    game.update()
    assert game.state is GameState.PAUSED
    assert game.snake.head == head


def test_unpause_resumes_movement(game: Game) -> None:
    game.apple.cell = (0, 0)
    game.handle(Command.TOGGLE_PAUSE)
    game.handle(Command.TOGGLE_PAUSE)
    game.update()
    assert game.state is GameState.RUNNING
    assert game.snake.head == (6, 5)


def test_turns_are_ignored_on_pause(game: Game) -> None:
    game.apple.cell = (0, 0)
    game.handle(Command.TOGGLE_PAUSE)
    game.handle(Command.TURN_UP)
    game.handle(Command.TOGGLE_PAUSE)
    game.update()
    assert game.snake.head == (6, 5)


def test_pause_is_unavailable_after_game_over(game: Game) -> None:
    crash_into_itself(game)
    game.handle(Command.TOGGLE_PAUSE)
    assert game.state is GameState.GAME_OVER


def test_restart_is_ignored_while_running(game: Game) -> None:
    feed_snake(game, 2)
    game.handle(Command.RESTART)
    assert game.score == 2
    assert game.state is GameState.RUNNING


def test_restart_is_ignored_on_pause(game: Game) -> None:
    feed_snake(game, 2)
    game.handle(Command.TOGGLE_PAUSE)
    game.handle(Command.RESTART)
    assert game.score == 2
    assert game.state is GameState.PAUSED


def test_restart_after_game_over_starts_new_round(game: Game) -> None:
    crash_into_itself(game)
    game.handle(Command.RESTART)
    assert game.state is GameState.RUNNING
    assert game.score == 0
    assert len(game.snake) == 1
    assert game.snake.head == game.board.center
    assert game.apple.cell not in game.snake.cells


def test_quit_command_is_not_a_game_matter(game: Game) -> None:
    head = game.snake.head
    game.handle(Command.QUIT)
    assert game.state is GameState.RUNNING
    assert game.snake.head == head
