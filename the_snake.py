from random import choice, randint
from typing import NoReturn

import pygame

# Псевдонимы типов:
type Position = tuple[int, int]
type Direction = tuple[int, int]
type RGBColor = tuple[int, int, int]

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
DEFAULT_POSITION: Position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: RGBColor = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR: RGBColor = (93, 216, 228)

# Цвет яблока
APPLE_COLOR: RGBColor = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR: RGBColor = (0, 255, 0)

# Цвет по умолчанию
DEFAULT_COLOR: RGBColor = (255, 255, 255)

# Скорость движения змейки:
SPEED: int = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(self, position: Position = DEFAULT_POSITION,
                 color: RGBColor = DEFAULT_COLOR) -> None:
        """Инициализирует игровой объект.

        Args:
            position: Начальная позиция объекта на игровом поле.
            color: Цвет объекта в формате RGB.
        """
        self.position: Position = position
        self.body_color: RGBColor = color

    def draw(self) -> NoReturn:
        """Отрисовывает игровой объект.

        Метод должен быть переопределён в дочернем классе.
        """
        raise NotImplementedError(
            'Метод draw() должен быть переопределён в подклассе'
        )

    def draw_cell(self, position: Position, color: RGBColor | None = None,
                  border: bool = True) -> None:
        """Рисует одну клетку сетки.

        Args:
            position: Позиция объекта на игровом поле.
            color: Цвет объекта в формате RGB.
            border: Граница объекта
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color or self.body_color, rect)
        if border:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Представляет яблоко на игровом поле."""

    def __init__(self) -> None:
        """Создаёт яблоко со случайной начальной позицией."""
        super().__init__(self.randomize_position(), APPLE_COLOR)

    @staticmethod
    def randomize_position(
            positions: list[Position] | None = None
    ) -> Position:
        """Генерирует случайную свободную позицию для яблока.

        Args:
            positions: Список занятых позиций.

        Returns:
            Координаты свободной позиции (x, y).
        """
        if positions is None:
            positions = [DEFAULT_POSITION]
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if (x, y) not in positions:
                return x, y

    def set_new_position(
            self,
            positions: list[Position] | None = None
    ) -> None:
        """Перемещает яблоко в новую случайную позицию.

        Args:
            positions: Список занятых позиций.
        """
        self.position = self.randomize_position(positions)

    def get_position(self) -> Position:
        """Возвращает текущую позицию яблока.

        Returns:
            Координаты яблока (x, y).
        """
        return self.position

    def draw(self) -> None:
        """Отрисовывает яблоко и его границы."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Представляет змейку и управляет её состоянием."""

    def __init__(self) -> None:
        """Создаёт змейку и устанавливает начальное состояние."""
        super().__init__(color=SNAKE_COLOR)
        self.reset(direction=RIGHT)

    def reset(self, direction: Direction | None = None) -> None:
        """Сбрасывает состояние змейки.

        Args:
            direction: Начальное направление движения.
                Если не задано, выбирается случайное направление.
        """
        self.positions: list[Position] = [self.position]
        self.length: int = len(self.positions)

        if direction is None:
            direction = choice((UP, DOWN, LEFT, RIGHT))

        self.direction: Direction = direction
        self.next_direction: Direction | None = None
        self.last: Position | None = None

    def get_head_position(self) -> Position:
        """Возвращает текущую позицию головы змейки.

        Returns:
            Координаты головы (x, y).
        """
        return self.positions[0]

    def get_snake_positions(self) -> list[Position]:
        """Возвращает позиции всех сегментов змейки.

        Returns:
            Список координат сегментов змейки.
        """
        return self.positions

    def grow(self) -> None:
        """Увеличивает длину змейки на один сегмент."""
        self.length += 1

    def move(self) -> None:
        """Перемещает змейку на одну клетку.

        Обновляет направление, добавляет новую позицию головы
        и при необходимости удаляет последний сегмент хвоста.
        """
        self.update_direction()
        self.last = None

        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
                    (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает все сегменты змейки.

        Если хвост переместился, очищает его предыдущую позицию.
        """
        for position in self.positions:
            self.draw_cell(position)

        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)

    def update_direction(self) -> None:
        """Применяет запланированное направление движения."""
        if self.next_direction is not None:
            self.direction, self.next_direction = self.next_direction, None

    def collides_with_self(self) -> bool:
        """Проверяет столкновение головы змейки с её телом.

        Returns:
            True, если голова пересекается с телом, иначе False.
        """
        return self.get_head_position() in self.get_snake_positions()[1:]


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает события клавиатуры и изменение направления.

    Args:
        game_object: Змейка, направление которой изменяется.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def check_snake_self_collision(snake: Snake) -> None:
    """Проверяет столкновение змейки с самой собой.

    При обнаружении столкновения сбрасывает состояние змейки.

    Args:
        snake: Экземпляр змейки для проверки.
    """
    if snake.collides_with_self():
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.reset()


def check_apple_eating(snake: Snake, apple: Apple) -> None:
    """Проверяет, съела ли змейка яблоко.

    При совпадении позиций увеличивает длину змейки
    и перемещает яблоко.

    Args:
        snake: Экземпляр змейки.
        apple: Экземпляр яблока.
    """
    if snake.get_head_position() == apple.get_position():
        snake.grow()
        apple.set_new_position(snake.get_snake_positions())


def main() -> None:
    """Запускает основной игровой цикл.

    Создаёт игровые объекты, обрабатывает ввод,
    обновляет состояние игры и выполняет отрисовку.
    """
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        # Тут опишите основную логику игры.
        handle_keys(snake)

        snake.move()

        check_snake_self_collision(snake)
        check_apple_eating(snake, apple)

        apple.draw()
        snake.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
