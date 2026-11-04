"""Игровые сущности: змейка и яблоко."""

import random
from collections import deque
from collections.abc import Iterable
from itertools import islice

from .geometry import Board, Cell, Direction


class Snake:
    """Змейка: хранит тело и отвечает за собственное движение."""

    def __init__(self, head: Cell, direction: Direction) -> None:
        """Создаёт змейку из одного сегмента.

        Args:
            head: Начальная клетка головы.
            direction: Начальное направление движения.
        """
        self._body: deque[Cell] = deque([head])
        self._direction: Direction = direction
        self._pending: Direction | None = None

    def __len__(self) -> int:
        """Возвращает длину змейки в сегментах."""
        return len(self._body)

    @property
    def head(self) -> Cell:
        """Клетка головы."""
        return self._body[0]

    @property
    def cells(self) -> tuple[Cell, ...]:
        """Клетки всех сегментов, начиная с головы."""
        return tuple(self._body)

    def steer(self, direction: Direction) -> None:
        """Запоминает новое направление до следующего шага.

        Мгновенный разворот на противоположное направление игнорируется.

        Args:
            direction: Желаемое направление движения.
        """
        if direction is not self._direction.opposite:
            self._pending = direction

    def next_head(self, board: Board) -> Cell:
        """Возвращает клетку, в которую попадёт голова на следующем шаге.

        Args:
            board: Поле, по которому движется змейка.
        """
        direction = (self._pending if self._pending is not None
                     else self._direction)
        return board.step(self.head, direction)

    def move(self, board: Board, grow: bool = False) -> None:
        """Сдвигает змейку на одну клетку.

        Args:
            board: Поле, по которому движется змейка.
            grow: Если True, хвост остаётся на месте и змейка растёт.
        """
        if self._pending is not None:
            self._direction, self._pending = self._pending, None
        self._body.appendleft(board.step(self.head, self._direction))
        if not grow:
            self._body.pop()

    def hits_itself(self) -> bool:
        """Проверяет, находится ли голова на одном из сегментов тела."""
        return self.head in islice(self._body, 1, None)


class Apple:
    """Яблоко: хранит свою клетку и умеет переходить на новую."""

    def __init__(self, cell: Cell) -> None:
        """Создаёт яблоко в заданной клетке.

        Args:
            cell: Клетка, в которой лежит яблоко.
        """
        self.cell: Cell = cell

    def relocate(self, board: Board, occupied: Iterable[Cell],
                 rng: random.Random) -> bool:
        """Перемещает яблоко в случайную свободную клетку.

        Args:
            board: Игровое поле.
            occupied: Занятые клетки, на которые яблоко попасть не может.
            rng: Источник случайных чисел.

        Returns:
            True, если свободная клетка нашлась, иначе False.
        """
        free = board.free_cells(occupied)
        if not free:
            return False
        self.cell = rng.choice(free)
        return True
