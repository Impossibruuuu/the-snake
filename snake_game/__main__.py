"""Точка входа: собирает объекты игры и запускает её."""

import pygame

from .app import Application
from .controls import PygameKeyboard
from .game import Game
from .geometry import Board
from .rendering import PygameRenderer
from .settings import Settings


def main() -> None:
    """Создаёт зависимости и запускает игровой цикл."""
    settings = Settings()
    pygame.init()
    try:
        game = Game(Board(settings.grid_width, settings.grid_height))
        Application(
            game=game,
            controls=PygameKeyboard(),
            renderer=PygameRenderer(settings),
            clock=pygame.time.Clock(),
            fps=settings.fps,
        ).run()
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
