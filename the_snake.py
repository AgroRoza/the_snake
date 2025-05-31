from random import choice, randint
from datetime import datetime
import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - серый:
BOARD_BACKGROUND_COLOR = (50, 50, 50)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейкин')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс, описывающий квадратные объекты - яблоко и блок змейки."""

    def __init__(self) -> None:
        self.body_color = None
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

    def draw(self):
        """
        Отрисовка квадратных объектов базового класса,
        переопределяется дальше по коду в других объектах
        """
        pass


class Apple(GameObject):
    """Описывает яблоко."""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def draw(self):
        """Отрисовывает яблоко - его позицию и цвета."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """При отрисовке яблока создаёт случайную позицию для него."""
        random_width_grid = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        random_heigth_grid = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (random_width_grid, random_heigth_grid)


class Snake(GameObject):
    """Отвечает за змейку, состоящую из движущихся квадратов."""

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.direction = RIGHT
        self.length = 1
        self.last = None
        self.next_direction = None
        self.positions = [self.position]

    def update_direction(self):
        """Обновляет направление перемещения змейки при нажатии на клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        new_position = (new_x, new_y)

        # Сохраняем последнюю позицию для затирания
        self.last = self.positions[-1] if len(self.positions) > 1 else None
        # Добавляем к змейке текущую её позицию
        self.positions.insert(0, new_position)
        """
        Если количество блоков змейки больше длинны с поправкой на первый
        блок - удаляем последний элемент из списка блоков змейки.
        """
        if len(self.positions) > self.length + 1:
            self.positions.pop()

    def draw(self):
        """
        Рисуем змейку - каждый блок из списка змейки, отдельно считаем
        голову и последний сегмент.
        """
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """
        Обсчитывает позицию головы змеи для дальнейшей проверки на коллизии
        с объектами.
        """
        return self.positions[0] if self.positions else self.position

    def game_over(self):
        """
        Перезапускает змейку при поражении, используя случайное направление
        движения и сохраняет результат длины в файл.
        """
        self.randomize_snake_direction()
        self.next_direction = None
        self.positions = [self.position]
        self.last = None
        self.results_file = 'results.txt'

        # Открыть на запись файл example.txt
        with open(self.results_file, 'a', encoding='utf-8') as cm:
            # Записать в файл строку.
            cm.write(
                f'Результат игры: {datetime.now()} вы достигли длины в {
                    self.length} блоков' + "\n")
        self.length = 1

    def randomize_snake_direction(self):
        """
        Выбираем случайное направление движения из доступных, используется
        после поражения.
        """
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        self.direction = choice(possible_directions)


def handle_keys(game_object):
    """
    Обрабатываем нажатие клавишь на клавиатуре, и защищаем от поворота на
    180 градусов и проигрыша.
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


def main():
    """Основное тело игры"""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        snake.update_direction()
        snake.move()

        # Проверка столкновения с яблоком.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
            # Убедимся, что яблоко не появилось в теле змейки.
            while apple.position in snake.positions:
                apple.randomize_position()

        # Проверка столкновения с собой.
        if snake.get_head_position() in snake.positions[1:]:
            snake.game_over()

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
