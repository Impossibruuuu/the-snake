"""Ввод: преобразует события pygame в команды игры."""

from collections.abc import Mapping
from typing import Protocol

import pygame

from .game import Command


class InputSource(Protocol):
    """Источник команд игрока."""

    def poll(self) -> list[Command]:
        """Возвращает команды, накопленные с прошлого вызова."""
        ...


DEFAULT_BINDINGS: Mapping[int, Command] = {
    pygame.K_UP: Command.TURN_UP,
    pygame.K_DOWN: Command.TURN_DOWN,
    pygame.K_LEFT: Command.TURN_LEFT,
    pygame.K_RIGHT: Command.TURN_RIGHT,
    pygame.K_ESCAPE: Command.TOGGLE_PAUSE,
    pygame.K_SPACE: Command.RESTART,
}


class PygameKeyboard:
    """Клавиатурный ввод на основе событий pygame."""

    def __init__(self,
                 bindings: Mapping[int, Command] = DEFAULT_BINDINGS) -> None:
        """Создаёт источник ввода.

        Args:
            bindings: Соответствие кодов клавиш и команд.
        """
        self._bindings: Mapping[int, Command] = bindings

    def poll(self) -> list[Command]:
        """Читает очередь событий pygame и возвращает команды."""
        commands: list[Command] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                commands.append(Command.QUIT)
            elif event.type == pygame.KEYDOWN:
                command = self._bindings.get(event.key)
                if command is not None:
                    commands.append(command)
        return commands
