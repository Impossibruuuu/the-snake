"""Дымовой тест точки входа: игра собирается и корректно завершается."""

import pygame
import pytest

from snake_game.__main__ import main
from snake_game.controls import PygameKeyboard
from snake_game.game import Command

pytestmark = pytest.mark.usefixtures('pygame_env')


@pytest.mark.timeout(10)
def test_main_starts_and_quits_cleanly(
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(PygameKeyboard, 'poll',
                        lambda self: [Command.QUIT])
    main()
    assert not pygame.get_init()
