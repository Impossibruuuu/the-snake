"""Вспомогательные функции для тестов игровой логики."""

from snake_game.game import Command, Game


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
