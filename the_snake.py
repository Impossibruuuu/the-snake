from random import randint, choice

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
DEFAULT_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет по умолчанию
DEFAULT_COLOR = (255, 255, 255)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    def __init__(self, position=DEFAULT_POSITION, color=DEFAULT_COLOR):
        self.position = position
        self.body_color = color

    def draw(self):
        raise NotImplementedError("Метод draw() должен быть переопределён в "
                                  "подклассе")


class Apple(GameObject):
    def __init__(self):
        super().__init__(self.randomize_position(), APPLE_COLOR)

    @staticmethod
    def randomize_position(positions=None):
        if positions is None:
            positions = [DEFAULT_POSITION]
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if (x, y) not in positions:
                return x, y

    def set_new_position(self, positions=None):
        self.position = self.randomize_position(positions)

    def get_position(self):
        return self.position

    def draw(self):
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    def __init__(self):
        super().__init__(color=SNAKE_COLOR)
        self.reset(direction=RIGHT)

    def reset(self, direction=None):
        self.positions = [self.position]
        self.length = len(self.positions)
        if direction is None:
            direction = choice((UP, DOWN, LEFT, RIGHT))
        self.direction = direction
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        return self.positions[0]

    def get_snake_positions(self):
        return self.positions

    def grow(self):
        self.length += 1

    def move(self):
        self.update_direction()
        self.last = None
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head_x, new_head_y = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
                                  (head_y + dy
                                   * GRID_SIZE) % SCREEN_HEIGHT)

        self.positions.insert(0, (new_head_x, new_head_y))

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента
        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        if self.next_direction is not None:
            self.direction, self.next_direction = self.next_direction, None

    def collides_with_self(self):
        return self.get_head_position() in self.get_snake_positions()[1:]


def handle_keys(game_object):
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


def check_snake_self_collision(snake):
    if snake.collides_with_self():
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.reset()


def check_apple_eating(snake, apple):
    if snake.get_head_position() == apple.get_position():
        snake.grow()
        apple.set_new_position(snake.get_snake_positions())


def main():
    # Тут нужно создать экземпляры классов.
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
