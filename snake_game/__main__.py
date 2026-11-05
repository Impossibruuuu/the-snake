"""Точка входа: собирает объекты игры и запускает её."""

import pygame

from .ai import AStarAI, BFSAI, GreedyAI
from .app import Application
from .controls import PygameKeyboard
from .game import Command, Game
from .geometry import Board
from .rendering import PygameRenderer
from .settings import Settings


def main() -> None:
    """Создаёт зависимости и запускает игровой цикл."""
    settings = Settings()
    pygame.init()
    try:
        game = Game(
            Board(settings.grid_width, settings.grid_height),
            controllers={
                Command.USE_PLAYER: None,
                Command.USE_GREEDY_AI: GreedyAI(),
                Command.USE_BFS_AI: BFSAI(),
                Command.USE_ASTAR_AI: AStarAI(),
            },
        )
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
