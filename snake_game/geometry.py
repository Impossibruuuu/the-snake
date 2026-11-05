"""Геометрия игрового поля: клетки, направления и границы."""

from collections.abc import Iterable
from enum import Enum
from typing import Self

type Cell = tuple[int, int]


class Direction(Enum):
    """Направление движения в координатах сетки."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def opposite(self) -> Self:
        """Возвращает противоположное направление."""
        dx, dy = self.value
        return type(self)((-dx, -dy))


class Board:
    """Прямоугольное поле без стен: края замкнуты друг на друга."""

    def __init__(self, width: int, height: int) -> None:
        """Создаёт поле заданного размера.

        Args:
            width: Ширина поля в клетках.
            height: Высота поля в клетках.

        Raises:
            ValueError: Если поле меньше 2×2 клеток.
        """
        if width < 2 or height < 2:
            raise ValueError('Поле должно быть не меньше 2×2 клеток')
        self.width: int = width
        self.height: int = height

    @property
    def center(self) -> Cell:
        """Клетка в центре поля."""
        return self.width // 2, self.height // 2

    def step(self, cell: Cell, direction: Direction) -> Cell:
        """Возвращает соседнюю клетку с учётом прохода сквозь границы.

        Args:
            cell: Исходная клетка.
            direction: Направление шага.

        Returns:
            Координаты клетки после шага.
        """
        x, y = cell
        dx, dy = direction.value
        return (x + dx) % self.width, (y + dy) % self.height

    def distance(self, first: Cell, second: Cell) -> int:
        """Возвращает число шагов между клетками без препятствий.

        Учитывает проход сквозь границы: по каждой оси выбирается
        более короткий путь, прямой или через край поля.

        Args:
            first: Первая клетка.
            second: Вторая клетка.
        """
        dx = abs(first[0] - second[0])
        dy = abs(first[1] - second[1])
        return min(dx, self.width - dx) + min(dy, self.height - dy)

    def free_cells(self, occupied: Iterable[Cell]) -> list[Cell]:
        """Возвращает все клетки поля, кроме занятых.

        Args:
            occupied: Занятые клетки.

        Returns:
            Список свободных клеток.
        """
        taken = set(occupied)
        return [(x, y)
                for y in range(self.height)
                for x in range(self.width)
                if (x, y) not in taken]
