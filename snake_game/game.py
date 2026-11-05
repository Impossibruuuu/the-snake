"""Игровая логика: состояния, команды и правила. Не зависит от pygame."""

import random
from collections.abc import Mapping
from enum import Enum, auto

from .ai import SnakeAI
from .entities import Apple, Snake
from .geometry import Board, Direction


class Command(Enum):
    """Команды игрока, не привязанные к конкретным клавишам."""

    TURN_UP = auto()
    TURN_DOWN = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    USE_PLAYER = auto()
    USE_GREEDY_AI = auto()
    USE_BFS_AI = auto()
    USE_ASTAR_AI = auto()
    TOGGLE_PAUSE = auto()
    RESTART = auto()
    QUIT = auto()


class GameState(Enum):
    """Режимы работы игры."""

    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


_TURNS: Mapping[Command, Direction] = {
    Command.TURN_UP: Direction.UP,
    Command.TURN_DOWN: Direction.DOWN,
    Command.TURN_LEFT: Direction.LEFT,
    Command.TURN_RIGHT: Direction.RIGHT,
}


class Game:
    """Хранит состояние партии и применяет к нему правила игры."""

    _state: GameState
    _score: int
    _snake: Snake
    _apple: Apple

    def __init__(
            self, board: Board, rng: random.Random | None = None,
            controllers: Mapping[Command, SnakeAI | None] | None = None,
    ) -> None:
        """Создаёт игру и сразу начинает первую партию.

        Args:
            board: Игровое поле.
            rng: Источник случайных чисел. Можно подставить
                детерминированный генератор для тестов.
            controllers: Режимы управления: команда выбора режима
                и соответствующий ей алгоритм. None означает ручное
                управление. Команды, которых здесь нет, игнорируются.
        """
        self._board: Board = board
        self._rng: random.Random = rng or random.Random()
        self._controllers: dict[Command, SnakeAI | None] = (
            dict(controllers) if controllers else {}
        )
        self._ai: SnakeAI | None = None
        self.restart()

    @property
    def board(self) -> Board:
        """Игровое поле."""
        return self._board

    @property
    def state(self) -> GameState:
        """Текущее состояние игры."""
        return self._state

    @property
    def score(self) -> int:
        """Количество съеденных яблок в текущей партии."""
        return self._score

    @property
    def snake(self) -> Snake:
        """Змейка текущей партии."""
        return self._snake

    @property
    def apple(self) -> Apple:
        """Яблоко текущей партии."""
        return self._apple

    @property
    def ai(self) -> SnakeAI | None:
        """Алгоритм, управляющий змейкой. None, если играет человек."""
        return self._ai

    def restart(self) -> None:
        """Начинает новую партию: сбрасывает счёт, змейку и яблоко.

        Выбранный режим управления сохраняется.
        """
        self._state = GameState.RUNNING
        self._score = 0
        self._snake = Snake(self._board.center, Direction.RIGHT)
        # Стартовая клетка яблока сразу заменяется случайной свободной.
        self._apple = Apple(self._board.center)
        self._apple.relocate(self._board, self._snake.cells, self._rng)

    def handle(self, command: Command) -> None:
        """Применяет команду игрока с учётом текущего состояния.

        Args:
            command: Команда, полученная от источника ввода.
        """
        if command in _TURNS:
            if self._state is GameState.RUNNING and self._ai is None:
                self._snake.steer(_TURNS[command])
        elif command in self._controllers:
            self._ai = self._controllers[command]
        elif command is Command.TOGGLE_PAUSE:
            self._toggle_pause()
        elif command is Command.RESTART:
            if self._state is GameState.GAME_OVER:
                self.restart()

    def update(self) -> None:
        """Выполняет один игровой шаг. На паузе и после конца игры
        ничего не делает.
        """
        if self._state is not GameState.RUNNING:
            return

        if self._ai is not None:
            self._snake.steer(self._ai.choose_direction(
                self._snake, self._apple.cell, self._board
            ))

        ate_apple = (self._snake.next_head(self._board)
                     == self._apple.cell)
        self._snake.move(self._board, grow=ate_apple)

        if self._snake.hits_itself():
            self._state = GameState.GAME_OVER
        elif ate_apple:
            self._score += 1
            has_room = self._apple.relocate(
                self._board, self._snake.cells, self._rng
            )
            if not has_room:
                # Змейка заполнила всё поле: играть дальше некуда.
                self._state = GameState.GAME_OVER

    def _toggle_pause(self) -> None:
        """Переключает паузу. На экране конца игры не действует."""
        if self._state is GameState.RUNNING:
            self._state = GameState.PAUSED
        elif self._state is GameState.PAUSED:
            self._state = GameState.RUNNING
