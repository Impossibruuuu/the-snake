"""Отрисовка игры средствами pygame."""

from collections.abc import Callable
from typing import Protocol

import pygame

from .game import Game, GameState
from .geometry import Cell
from .settings import RGBColor, Settings


class Renderer(Protocol):
    """Отображает текущее состояние игры."""

    def render(self, game: Game) -> None:
        """Рисует кадр.

        Args:
            game: Игра, состояние которой нужно показать.
        """
        ...


class PygameRenderer:
    """Рисует поле, змейку, яблоко и экраны паузы и конца игры."""

    def __init__(self, settings: Settings) -> None:
        """Создаёт окно и подготавливает шрифты и затемнение.

        Args:
            settings: Настройки игры.
        """
        self._settings: Settings = settings
        size = (settings.screen_width, settings.screen_height)
        self._screen: pygame.Surface = pygame.display.set_mode(size)
        self._center: tuple[int, int] = (size[0] // 2, size[1] // 2)
        self._title_font = pygame.font.Font(None, settings.title_font_size)
        self._info_font = pygame.font.Font(None, settings.info_font_size)
        self._dimmer: pygame.Surface = pygame.Surface(size)
        self._dimmer.fill(settings.palette.background)
        self._dimmer.set_alpha(settings.overlay_alpha)
        self._caption: str | None = None
        self._overlays: dict[GameState, Callable[[Game], None]] = {
            GameState.PAUSED: self._draw_pause,
            GameState.GAME_OVER: self._draw_game_over,
        }

    def render(self, game: Game) -> None:
        """Рисует кадр и обновляет заголовок окна со счётом.

        Args:
            game: Игра, состояние которой нужно показать.
        """
        palette = self._settings.palette
        self._screen.fill(palette.background)
        self._draw_cell(game.apple.cell, palette.apple)
        for cell in game.snake.cells:
            self._draw_cell(cell, palette.snake)

        overlay = self._overlays.get(game.state)
        if overlay is not None:
            overlay(game)

        self._update_caption(game)
        pygame.display.update()

    def _draw_cell(self, cell: Cell, color: RGBColor) -> None:
        """Рисует одну клетку с рамкой."""
        size = self._settings.cell_size
        rect = pygame.Rect(cell[0] * size, cell[1] * size, size, size)
        pygame.draw.rect(self._screen, color, rect)
        pygame.draw.rect(self._screen, self._settings.palette.border,
                         rect, 1)

    def _draw_text(self, text: str, font: pygame.font.Font,
                   center: tuple[int, int]) -> None:
        """Выводит строку текста с центром в заданной точке."""
        surface = font.render(text, True, self._settings.palette.text)
        self._screen.blit(surface, surface.get_rect(center=center))

    def _draw_pause(self, game: Game) -> None:
        """Затемняет поле и выводит надпись паузы."""
        self._screen.blit(self._dimmer, (0, 0))
        self._draw_text(self._settings.texts.pause,
                        self._title_font, self._center)

    def _draw_game_over(self, game: Game) -> None:
        """Затемняет поле и выводит итог партии."""
        texts = self._settings.texts
        offset = self._settings.line_offset
        center_x, center_y = self._center

        self._screen.blit(self._dimmer, (0, 0))
        self._draw_text(texts.game_over, self._title_font,
                        (center_x, center_y - offset))
        self._draw_text(f'{texts.score}: {game.score}',
                        self._info_font, self._center)
        self._draw_text(texts.restart_hint, self._info_font,
                        (center_x, center_y + offset))

    def _update_caption(self, game: Game) -> None:
        """Обновляет заголовок окна: счёт и режим управления.

        Заголовок меняется только при изменении текста.
        """
        texts = self._settings.texts
        if game.ai is None:
            ai_state = texts.ai_off
        else:
            ai_state = f'{texts.ai_on} ({game.ai.name})'
        caption = (f'{self._settings.window_title}  |  '
                   f'{texts.caption_score}: {game.score}  |  '
                   f'{texts.ai_label}: {ai_state}')
        if caption != self._caption:
            pygame.display.set_caption(caption)
            self._caption = caption
