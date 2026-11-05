"""Алгоритмы управления змейкой. Не зависят от pygame."""

from abc import ABC, abstractmethod
from collections import deque
from heapq import heappop, heappush
from itertools import count
from typing import ClassVar

from .entities import Snake
from .geometry import Board, Cell, Direction


class SnakeAI(ABC):
    """Алгоритм, который выбирает направление движения змейки."""

    name: ClassVar[str]

    @abstractmethod
    def choose_direction(self, snake: Snake, target: Cell,
                         board: Board) -> Direction:
        """Выбирает направление для следующего шага.

        Змейку метод не изменяет.

        Args:
            snake: Управляемая змейка.
            target: Клетка, к которой нужно прийти (яблоко).
            board: Игровое поле.

        Returns:
            Выбранное направление. Если безопасных ходов нет,
            возвращается текущее направление змейки.
        """


def _safe_moves(snake: Snake, board: Board) -> list[tuple[Direction, Cell]]:
    """Возвращает ходы из головы, не ведущие в тело и не назад."""
    blocked = set(snake.cells)
    reverse = snake.direction.opposite
    moves: list[tuple[Direction, Cell]] = []
    for direction in Direction:
        if direction is reverse:
            continue
        cell = board.step(snake.head, direction)
        if cell not in blocked:
            moves.append((direction, cell))
    return moves


def _fallback(snake: Snake, board: Board) -> Direction:
    """Выбирает ход, когда пути к цели нет.

    Сначала пробует ехать прямо, затем любой безопасный ход.
    """
    directions = [direction for direction, _ in _safe_moves(snake, board)]
    if snake.direction in directions or not directions:
        return snake.direction
    return directions[0]


class GreedyAI(SnakeAI):
    """Жадный алгоритм: каждый шаг приближает голову к цели."""

    name = 'Greedy'

    def choose_direction(self, snake: Snake, target: Cell,
                         board: Board) -> Direction:
        """Выбирает направление для следующего шага.

        Змейку метод не изменяет.

        Args:
            snake: Управляемая змейка.
            target: Клетка, к которой нужно прийти (яблоко).
            board: Игровое поле.

        Returns:
            Выбранное направление. Если безопасных ходов нет,
            возвращается текущее направление змейки.
        """
        moves = _safe_moves(snake, board)
        if not moves:
            return snake.direction
        direction, _ = min(
            moves, key=lambda move: board.distance(move[1], target)
        )
        return direction


class BFSAI(SnakeAI):
    """Поиск в ширину: кратчайший путь к цели в обход тела змейки."""

    name = 'BFS'

    def choose_direction(self, snake: Snake, target: Cell,
                         board: Board) -> Direction:
        """Выбирает направление для следующего шага.

        Змейку метод не изменяет.

        Args:
            snake: Управляемая змейка.
            target: Клетка, к которой нужно прийти (яблоко).
            board: Игровое поле.

        Returns:
            Выбранное направление. Если безопасных ходов нет,
            возвращается текущее направление змейки.
        """
        blocked = set(snake.cells)
        # Для каждой достигнутой клетки хранится первый шаг пути к ней.
        first_step: dict[Cell, Direction] = {
            cell: direction
            for direction, cell in _safe_moves(snake, board)
        }
        queue = deque(first_step)

        while queue:
            current = queue.popleft()
            if current == target:
                return first_step[current]
            for direction in Direction:
                neighbor = board.step(current, direction)
                if neighbor not in first_step and neighbor not in blocked:
                    first_step[neighbor] = first_step[current]
                    queue.append(neighbor)

        return _fallback(snake, board)


class AStarAI(SnakeAI):
    """Поиск A*: кратчайший путь с эвристикой расстояния до цели."""

    name = 'A*'

    def choose_direction(self, snake: Snake, target: Cell,
                         board: Board) -> Direction:
        """Выбирает направление для следующего шага.

        Змейку метод не изменяет.

        Args:
            snake: Управляемая змейка.
            target: Клетка, к которой нужно прийти (яблоко).
            board: Игровое поле.

        Returns:
            Выбранное направление. Если безопасных ходов нет,
            возвращается текущее направление змейки.
        """
        blocked = set(snake.cells)
        cost: dict[Cell, int] = {}
        first_step: dict[Cell, Direction] = {}
        tie_breaker = count()
        frontier: list[tuple[int, int, Cell]] = []

        for direction, cell in _safe_moves(snake, board):
            cost[cell] = 1
            first_step[cell] = direction
            priority = 1 + board.distance(cell, target)
            heappush(frontier, (priority, next(tie_breaker), cell))

        while frontier:
            _, _, current = heappop(frontier)
            if current == target:
                return first_step[current]
            for direction in Direction:
                neighbor = board.step(current, direction)
                if neighbor in blocked:
                    continue
                new_cost = cost[current] + 1
                if neighbor not in cost or new_cost < cost[neighbor]:
                    cost[neighbor] = new_cost
                    first_step[neighbor] = first_step[current]
                    priority = new_cost + board.distance(neighbor, target)
                    heappush(frontier,
                             (priority, next(tie_breaker), neighbor))

        return _fallback(snake, board)
