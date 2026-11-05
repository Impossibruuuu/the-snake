"""Вспомогательные функции для тестов игровой логики."""

from snake_game.ai import SnakeAI
from snake_game.entities import Snake
from snake_game.game import Command, Game
from snake_game.geometry import Board, Cell, Direction


class FixedAI(SnakeAI):
    """Подставной алгоритм: всегда выбирает одно и то же направление."""

    name = 'Fixed'

    def __init__(self, direction: Direction) -> None:
        self._direction = direction

    def choose_direction(self, snake: Snake, target: Cell,
                         board: Board) -> Direction:
        return self._direction


def feed_snake(game: Game, apples: int) -> None:
    """Скармливает змейке яблоки: каждое кладётся прямо по курсу."""
    for _ in range(apples):
        game.apple.cell = game.snake.next_head(game.board)
        game.update()


def crash_into_itself(game: Game) -> None:
    """Отращивает змейку до 5 сегментов и заставляет её укусить себя.

    Рассчитано на поле, где вокруг центра есть место для петли
    (например, 10×10).
    """
    feed_snake(game, 4)
    game.apple.cell = (0, 0)
    for command in (Command.TURN_DOWN, Command.TURN_LEFT, Command.TURN_UP):
        game.handle(command)
        game.update()
