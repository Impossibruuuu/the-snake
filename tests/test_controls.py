"""Тесты ввода: события pygame превращаются в команды игры."""

from collections.abc import Iterator

import pygame
import pytest

from snake_game.controls import DEFAULT_BINDINGS, PygameKeyboard
from snake_game.game import Command

pytestmark = pytest.mark.usefixtures('pygame_env')


@pytest.fixture(autouse=True)
def empty_event_queue(pygame_env: None) -> Iterator[None]:
    """Очищает очередь событий до и после теста."""
    pygame.event.clear()
    yield
    pygame.event.clear()


def press(key: int) -> None:
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))


@pytest.mark.parametrize(('key', 'command'), [
    (pygame.K_UP, Command.TURN_UP),
    (pygame.K_DOWN, Command.TURN_DOWN),
    (pygame.K_LEFT, Command.TURN_LEFT),
    (pygame.K_RIGHT, Command.TURN_RIGHT),
    (pygame.K_ESCAPE, Command.TOGGLE_PAUSE),
    (pygame.K_SPACE, Command.RESTART),
])
def test_default_key_bindings(key: int, command: Command) -> None:
    press(key)
    assert PygameKeyboard().poll() == [command]


def test_window_close_becomes_quit_command() -> None:
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    assert PygameKeyboard().poll() == [Command.QUIT]


def test_unbound_key_is_ignored() -> None:
    press(pygame.K_q)
    assert PygameKeyboard().poll() == []


def test_key_release_is_ignored() -> None:
    pygame.event.post(pygame.event.Event(pygame.KEYUP,
                                         key=pygame.K_UP))
    assert PygameKeyboard().poll() == []


def test_order_of_commands_is_preserved() -> None:
    for key in (pygame.K_UP, pygame.K_LEFT, pygame.K_ESCAPE):
        press(key)
    assert PygameKeyboard().poll() == [
        Command.TURN_UP, Command.TURN_LEFT, Command.TOGGLE_PAUSE,
    ]


def test_poll_consumes_the_events() -> None:
    press(pygame.K_UP)
    keyboard = PygameKeyboard()
    keyboard.poll()
    assert keyboard.poll() == []


def test_bindings_can_be_replaced() -> None:
    keyboard = PygameKeyboard({pygame.K_w: Command.TURN_UP})
    press(pygame.K_w)
    press(pygame.K_UP)
    assert keyboard.poll() == [Command.TURN_UP]


def test_every_gameplay_command_has_a_default_key() -> None:
    bound = set(DEFAULT_BINDINGS.values())
    assert bound == set(Command) - {Command.QUIT}
