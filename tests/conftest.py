"""Общие фикстуры. pygame работает через «пустые» драйверы SDL."""

import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import random  # noqa: E402
from collections.abc import Iterator  # noqa: E402

import pygame  # noqa: E402
import pytest  # noqa: E402

from snake_game.game import Game  # noqa: E402
from snake_game.geometry import Board  # noqa: E402
from snake_game.settings import Settings  # noqa: E402


@pytest.fixture
def pygame_env() -> Iterator[None]:
    """Инициализирует pygame на время одного теста."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def board() -> Board:
    """Поле 10×10: центр в клетке (5, 5)."""
    return Board(10, 10)


@pytest.fixture
def game(board: Board) -> Game:
    """Игра с детерминированным генератором случайных чисел."""
    return Game(board, random.Random(0))


@pytest.fixture
def settings() -> Settings:
    """Настройки игры по умолчанию."""
    return Settings()
