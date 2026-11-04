"""Приложение: связывает ввод, игру и отрисовку в один цикл."""

from typing import Protocol

from .controls import InputSource
from .game import Command, Game
from .rendering import Renderer


class FrameClock(Protocol):
    """Ограничитель частоты кадров."""

    def tick(self, framerate: float = 0) -> int:
        """Ждёт до следующего кадра, не превышая заданную частоту."""
        ...


class Application:
    """Главный цикл игры. Сам ничего не знает о pygame."""

    def __init__(self, game: Game, controls: InputSource,
                 renderer: Renderer, clock: FrameClock, fps: int) -> None:
        """Собирает приложение из готовых частей.

        Args:
            game: Игровая логика.
            controls: Источник команд игрока.
            renderer: Объект, рисующий состояние игры.
            clock: Ограничитель частоты кадров.
            fps: Целевая частота кадров.
        """
        self._game: Game = game
        self._controls: InputSource = controls
        self._renderer: Renderer = renderer
        self._clock: FrameClock = clock
        self._fps: int = fps

    def run(self) -> None:
        """Запускает цикл и работает до команды выхода."""
        while True:
            self._clock.tick(self._fps)

            for command in self._controls.poll():
                if command is Command.QUIT:
                    return
                self._game.handle(command)

            self._game.update()
            self._renderer.render(self._game)
