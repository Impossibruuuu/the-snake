"""Тесты правил игры. Окно pygame для них не нужно."""

import random

import pytest

from snake_game.game import Command, Game, GameState
from snake_game.geometry import Board, Cell, Direction
from tests.helpers import FixedAI, crash_into_itself, feed_snake


@pytest.fixture
def ai_game(board: Board) -> Game:
    """Игра с режимами: игрок, «всегда вверх» и «всегда вниз»."""
    controllers = {
        Command.USE_PLAYER: None,
        Command.USE_GREEDY_AI: FixedAI(Direction.UP),
        Command.USE_BFS_AI: FixedAI(Direction.DOWN),
    }
    game = Game(board, random.Random(0), controllers)
    game.apple.cell = (0, 0)
    return game


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


def test_player_controls_the_snake_by_default(ai_game: Game) -> None:
    assert ai_game.ai is None


def test_selected_ai_drives_the_snake(ai_game: Game) -> None:
    ai_game.handle(Command.USE_GREEDY_AI)
    assert ai_game.ai is not None
    assert ai_game.ai.name == 'Fixed'
    ai_game.update()
    assert ai_game.snake.head == (5, 4)


def test_ai_can_be_replaced_by_another_one(ai_game: Game) -> None:
    ai_game.handle(Command.USE_GREEDY_AI)
    ai_game.handle(Command.USE_BFS_AI)
    ai_game.update()
    assert ai_game.snake.head == (5, 6)


def test_player_command_returns_manual_control(ai_game: Game) -> None:
    ai_game.handle(Command.USE_GREEDY_AI)
    ai_game.handle(Command.USE_PLAYER)
    assert ai_game.ai is None
    ai_game.update()
    assert ai_game.snake.head == (6, 5)


def test_arrow_keys_are_ignored_while_ai_plays(ai_game: Game) -> None:
    ai_game.handle(Command.USE_BFS_AI)
    ai_game.handle(Command.TURN_UP)
    ai_game.update()
    assert ai_game.snake.head == (5, 6)


def test_arrow_keys_work_again_after_switching_to_player(
        ai_game: Game) -> None:
    ai_game.handle(Command.USE_BFS_AI)
    ai_game.handle(Command.USE_PLAYER)
    ai_game.handle(Command.TURN_UP)
    ai_game.update()
    assert ai_game.snake.head == (5, 4)


def test_ai_choice_survives_restart(ai_game: Game) -> None:
    crash_into_itself(ai_game)
    ai_game.handle(Command.USE_GREEDY_AI)
    ai_game.handle(Command.RESTART)
    assert ai_game.state is GameState.RUNNING
    assert ai_game.ai is not None


def test_ai_can_be_switched_on_pause(ai_game: Game) -> None:
    ai_game.handle(Command.TOGGLE_PAUSE)
    ai_game.handle(Command.USE_GREEDY_AI)
    head = ai_game.snake.head
    ai_game.update()
    assert ai_game.ai is not None
    assert ai_game.snake.head == head


def test_ai_commands_are_ignored_without_controllers(game: Game) -> None:
    game.handle(Command.USE_BFS_AI)
    assert game.ai is None


def test_arrow_key_does_not_leak_through_when_ai_move_is_refused(
        board: Board) -> None:
    # AI просит разворот назад, змейка его игнорирует. Нажатая в этот
    # момент стрелка не должна подхватиться вместо хода AI.
    game = Game(board, random.Random(0),
                {Command.USE_BFS_AI: FixedAI(Direction.LEFT)})
    game.apple.cell = (0, 0)
    game.handle(Command.USE_BFS_AI)
    game.handle(Command.TURN_UP)
    game.update()
    assert game.snake.head == (6, 5)
