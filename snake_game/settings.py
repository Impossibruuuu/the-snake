"""Настройки игры: размеры поля, цвета, тексты и скорость."""

from dataclasses import dataclass, field

type RGBColor = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class Palette:
    """Цветовая схема игры."""

    background: RGBColor = (0, 0, 0)
    border: RGBColor = (93, 216, 228)
    snake: RGBColor = (0, 255, 0)
    apple: RGBColor = (255, 0, 0)
    text: RGBColor = (255, 255, 255)


@dataclass(frozen=True, slots=True)
class Texts:
    """Надписи на экранах игры."""

    pause: str = 'ПАУЗА'
    game_over: str = 'GAME OVER'
    score: str = 'СЧЁТ'
    restart_hint: str = 'PRESS SPACE TO RESTART'


@dataclass(frozen=True, slots=True)
class Settings:
    """Неизменяемые настройки игры.

    Размеры поля заданы в клетках, в пиксели они переводятся
    только при отрисовке.
    """

    cell_size: int = 20
    grid_width: int = 32
    grid_height: int = 24
    fps: int = 20
    window_title: str = 'Snake by Mark Lee'
    title_font_size: int = 96
    info_font_size: int = 48
    line_offset: int = 60
    overlay_alpha: int = 150
    palette: Palette = field(default_factory=Palette)
    texts: Texts = field(default_factory=Texts)

    @property
    def screen_width(self) -> int:
        """Ширина окна в пикселях."""
        return self.grid_width * self.cell_size

    @property
    def screen_height(self) -> int:
        """Высота окна в пикселях."""
        return self.grid_height * self.cell_size
