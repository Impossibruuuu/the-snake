"""Тесты отрисовки: проверяем реальные пиксели в окне без экрана."""

import random

import pygame
import pytest

from snake_game.ai import AStarAI, BFSAI
from snake_game.game import Command, Game
from snake_game.geometry import Board, Cell
from snake_game.rendering import PygameRenderer
from snake_game.settings import Palette, Settings
from tests.helpers import crash_into_itself, feed_snake

pytestmark = pytest.mark.usefixtures('pygame_env')

type Pixel = tuple[int, int, int]


@pytest.fixture
def renderer(settings: Settings) -> PygameRenderer:
    return PygameRenderer(settings)


def pixel_at_cell_center(settings: Settings, cell: Cell) -> Pixel:
    """Цвет центра клетки (рамка по краям не мешает)."""
    size = settings.cell_size
    x, y = cell[0] * size + size // 2, cell[1] * size + size // 2
    r, g, b, _ = pygame.display.get_surface().get_at((x, y))
    return r, g, b


def count_pixels(color: Pixel, around: tuple[int, int],
                 width: int = 300, height: int = 40) -> int:
    """Считает пиксели заданного цвета в прямоугольнике вокруг точки."""
    surface = pygame.display.get_surface()
    rect = pygame.Rect(0, 0, width, height)
    rect.center = around
    return sum(
        1
        for x in range(rect.left, rect.right)
        for y in range(rect.top, rect.bottom)
        if tuple(surface.get_at((x, y)))[:3] == color
    )


def test_window_has_configured_size(renderer: PygameRenderer,
                                    settings: Settings) -> None:
    assert pygame.display.get_surface().get_size() == (
        settings.screen_width, settings.screen_height)


def test_snake_apple_and_background_colors(
        renderer: PygameRenderer, game: Game, settings: Settings) -> None:
    renderer.render(game)
    palette = settings.palette
    occupied = [*game.snake.cells, game.apple.cell]
    empty = game.board.free_cells(occupied)[0]

    assert pixel_at_cell_center(settings, game.snake.head) == palette.snake
    assert pixel_at_cell_center(settings, game.apple.cell) == palette.apple
    assert pixel_at_cell_center(settings, empty) == palette.background


def test_every_snake_segment_is_drawn(
        renderer: PygameRenderer, game: Game, settings: Settings) -> None:
    feed_snake(game, 3)
    renderer.render(game)
    for cell in game.snake.cells:
        assert (pixel_at_cell_center(settings, cell)
                == settings.palette.snake)


def test_cell_border_uses_border_color(
        renderer: PygameRenderer, game: Game, settings: Settings) -> None:
    renderer.render(game)
    x, y = (game.snake.head[0] * settings.cell_size,
            game.snake.head[1] * settings.cell_size)
    r, g, b, _ = pygame.display.get_surface().get_at((x, y))
    assert (r, g, b) == settings.palette.border


def test_custom_palette_is_respected() -> None:
    custom = Settings(palette=Palette(apple=(1, 2, 3), snake=(4, 5, 6)))
    custom_game = Game(Board(custom.grid_width, custom.grid_height))
    PygameRenderer(custom).render(custom_game)
    assert (pixel_at_cell_center(custom, custom_game.apple.cell)
            == (1, 2, 3))
    assert (pixel_at_cell_center(custom, custom_game.snake.head)
            == (4, 5, 6))


def test_snake_leaves_no_trail(
        renderer: PygameRenderer, game: Game, settings: Settings) -> None:
    game.apple.cell = (0, 0)
    start = game.snake.head
    renderer.render(game)
    game.update()
    renderer.render(game)
    assert (pixel_at_cell_center(settings, start)
            == settings.palette.background)


def test_pause_dims_the_field_and_shows_text(
        renderer: PygameRenderer, game: Game, settings: Settings) -> None:
    center = (settings.screen_width // 2, settings.screen_height // 2)
    white = settings.palette.text

    renderer.render(game)
    assert count_pixels(white, center) == 0
    bright_apple = pixel_at_cell_center(settings, game.apple.cell)

    game.handle(Command.TOGGLE_PAUSE)
    renderer.render(game)
    dimmed_apple = pixel_at_cell_center(settings, game.apple.cell)
    assert dimmed_apple[0] < bright_apple[0]
    assert count_pixels(white, center) > 0


def test_game_over_shows_three_lines_of_text(
        renderer: PygameRenderer, game: Game, settings: Settings) -> None:
    crash_into_itself(game)
    renderer.render(game)

    center_x = settings.screen_width // 2
    center_y = settings.screen_height // 2
    white = settings.palette.text
    for offset in (-settings.line_offset, 0, settings.line_offset):
        assert count_pixels(white, (center_x, center_y + offset),
                            width=200, height=20) > 0


def test_caption_shows_title_score_and_ai_off(
        renderer: PygameRenderer, game: Game, settings: Settings) -> None:
    renderer.render(game)
    assert pygame.display.get_caption()[0] == (
        f'{settings.window_title}  |  Score: 0  |  AI: Off')

    feed_snake(game, 2)
    renderer.render(game)
    assert pygame.display.get_caption()[0] == (
        f'{settings.window_title}  |  Score: 2  |  AI: Off')


def test_caption_shows_ai_type_when_ai_is_on(
        renderer: PygameRenderer, board: Board,
        settings: Settings) -> None:
    ai_game = Game(board, random.Random(0), {
        Command.USE_PLAYER: None,
        Command.USE_BFS_AI: BFSAI(),
        Command.USE_ASTAR_AI: AStarAI(),
    })

    ai_game.handle(Command.USE_BFS_AI)
    renderer.render(ai_game)
    assert pygame.display.get_caption()[0] == (
        f'{settings.window_title}  |  Score: 0  |  AI: On (BFS)')

    ai_game.handle(Command.USE_ASTAR_AI)
    renderer.render(ai_game)
    assert pygame.display.get_caption()[0].endswith('AI: On (A*)')

    ai_game.handle(Command.USE_PLAYER)
    renderer.render(ai_game)
    assert pygame.display.get_caption()[0].endswith('AI: Off')
