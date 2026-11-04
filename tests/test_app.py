"""Тесты цикла приложения на подставных зависимостях (без pygame)."""

import pytest

from snake_game.app import Application
from snake_game.game import Command, Game, GameState
from snake_game.geometry import Cell


class ScriptedInput:
    """Выдаёт команды по кадрам; когда сценарий кончился - QUIT."""

    def __init__(self, *frames: list[Command]) -> None:
        self._frames = iter(frames)

    def poll(self) -> list[Command]:
        return next(self._frames, [Command.QUIT])


class RecordingRenderer:
    """Запоминает, что ей показали."""

    def __init__(self) -> None:
        self.frames: list[tuple[GameState, Cell]] = []

    def render(self, game: Game) -> None:
        self.frames.append((game.state, game.snake.head))


class RecordingClock:
    """Запоминает запрошенную частоту кадров и не ждёт."""

    def __init__(self) -> None:
        self.framerates: list[float] = []

    def tick(self, framerate: float = 0) -> int:
        self.framerates.append(framerate)
        return 0


def build(game: Game, *frames: list[Command],
          fps: int = 7) -> tuple[Application, RecordingRenderer,
                                 RecordingClock]:
    renderer, clock = RecordingRenderer(), RecordingClock()
    app = Application(game, ScriptedInput(*frames), renderer, clock, fps)
    return app, renderer, clock


@pytest.mark.timeout(5)
def test_each_frame_updates_game_and_renders(game: Game) -> None:
    game.apple.cell = (0, 0)
    app, renderer, _ = build(game, [], [], [])
    app.run()
    assert [head for _, head in renderer.frames] == [
        (6, 5), (7, 5), (8, 5)]


@pytest.mark.timeout(5)
def test_clock_is_ticked_with_configured_fps(game: Game) -> None:
    app, _, clock = build(game, [], [], fps=13)
    app.run()
    assert clock.framerates == [13, 13, 13]


@pytest.mark.timeout(5)
def test_quit_stops_the_loop_before_the_frame(game: Game) -> None:
    app, renderer, _ = build(game, [Command.QUIT])
    app.run()
    assert renderer.frames == []
    assert game.snake.head == game.board.center


@pytest.mark.timeout(5)
def test_commands_are_passed_to_the_game(game: Game) -> None:
    game.apple.cell = (0, 0)
    app, renderer, _ = build(
        game,
        [Command.TOGGLE_PAUSE], [],
        [Command.TOGGLE_PAUSE], [],
    )
    app.run()
    assert renderer.frames == [
        (GameState.PAUSED, (5, 5)),
        (GameState.PAUSED, (5, 5)),
        (GameState.RUNNING, (6, 5)),
        (GameState.RUNNING, (7, 5)),
    ]


@pytest.mark.timeout(5)
def test_turn_command_changes_course_in_the_same_frame(
        game: Game) -> None:
    game.apple.cell = (0, 0)
    app, renderer, _ = build(game, [Command.TURN_UP])
    app.run()
    assert renderer.frames == [(GameState.RUNNING, (5, 4))]
