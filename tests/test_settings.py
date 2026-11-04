"""Тесты настроек."""

import dataclasses

import pytest

from snake_game.settings import Palette, Settings


def test_default_window_size_is_640_by_480(settings: Settings) -> None:
    assert (settings.screen_width, settings.screen_height) == (640, 480)


def test_window_size_follows_grid_and_cell_size() -> None:
    custom = Settings(cell_size=10, grid_width=8, grid_height=6)
    assert (custom.screen_width, custom.screen_height) == (80, 60)


def test_settings_are_immutable(settings: Settings) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.fps = 60  # type: ignore[misc]


def test_palette_can_be_replaced() -> None:
    custom = Settings(palette=Palette(apple=(1, 2, 3)))
    assert custom.palette.apple == (1, 2, 3)
    assert custom.palette.snake == Palette().snake
