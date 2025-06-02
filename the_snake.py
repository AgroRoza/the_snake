from datetime import datetime
from random import choice, randint

import pygame as pg

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
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейкин')

# Настройка времени:
clock = pg.time.Clock()

# Центер экрана:
SCREEN_CENTER = (SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)


class GameObject:
    """Базовый класс, описывающий квадратные объекты - яблоко и блок змейки."""

    def __init__(
            self,
            body_color=None,
            position=SCREEN_CENTER
    ) -> None:
        self.body_color = body_color
        self.position = position

    def draw(self):
        """
        Отрисовка квадратных объектов базового класса,
        переопределяется дальше по коду в других объектах
        """
        raise NotImplementedError(
            'Метод draw() должен быть переопределён в дочерних классах'
        )

    def draw_rect(self, position=None, body_color=None):
        """Рисуем ячейку с рамкой в заданой позиции заданым цветом"""
        rect = pg.Rect(position or self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color or self.body_color, rect)
        pg.draw.rect(screen, body_color or BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Отвечает за змейку, состоящую из движущихся квадратов."""

    def __init__(
            self,
            body_color=SNAKE_COLOR,
            position=SCREEN_CENTER
    ):
        super().__init__(body_color, position)
        self.reset()

    # def update_direction(self):
    #     """Обновляет направление перемещения змейки при нажатии на клавиши."""
    #     if self.next_direction:
    #         self.direction = self.next_direction
    #         self.next_direction = None

    def update_direction(self, next_direction):
        """Обновляет направление перемещения змейки при нажатии на клавиши."""
        if next_direction:
            self.direction = next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        new_position = (new_x, new_y)

        # Сохраняем последнюю позицию для затирания
        self.last = self.positions.pop()

        # Добавляем к змейке текущую её позицию
        self.positions.insert(0, new_position)

    def draw(self):
        """
        Рисуем змейку - каждый блок из списка змейки, отдельно считаем
        голову и последний сегмент.
        """
        for position in self.positions:
            self.draw_rect(position)

        # Затирание последнего сегмента
        if self.last:
            self.draw_rect(self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """
        Обсчитывает позицию головы змеи для дальнейшей проверки на коллизии
        с объектами.
        """
        return self.positions[0]

    def reset(self):
        """
        Перезапускает змейку при поражении, используя случайное направление
        движения.
        """
        self.randomize_snake_direction()
        self.next_direction = None
        self.positions = [self.position]
        self.last = None

    def randomize_snake_direction(self):
        """
        Выбираем случайное направление движения из доступных, используется
        после поражения.
        """
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        self.direction = choice(possible_directions)

    def grow(self):
        """Увеличивает длину змейки."""
        self.positions.append(self.last)
        self.last = None


class Apple(GameObject):
    """Описывает яблоко."""

    # Изначально я сделал snake=None, игра работала, но тесты не проходили.
    def __init__(
            self,
            snake=Snake(),
            position=None,
            body_color=APPLE_COLOR,
    ):
        super().__init__(body_color)
        self.snake = snake
        # Позволяет передать желаемую позицию яблока при его отображении.
        if not position:
            self.randomize_position()
        else:
            self.position = position

    def draw(self):
        """Отрисовывает яблоко - его позицию и цвета."""
        self.draw_rect()

    def randomize_position(self):
        """
        При отрисовке яблока создаёт случайную позицию для него.
        Учитывает текущее положение змейки чтобя яблоко не появилось внутри.
        """
        new_position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        if new_position in self.snake.positions:
            self.randomize_position()
        else:
            self.position = new_position


def end_game(score, snake):
    """
    Завершает текущую попытку, сохраняя результат в файл и перезапускает
    змейку
    """
    results_file = 'results.txt'
    current_date = datetime.now().strftime('%d.%m.%Y, %H:%M:%S')

    # Открыть на запись файл example.txt
    with open(results_file, 'a', encoding='utf-8') as cm:
        # Записать в файл строку.
        cm.write(
            f'Результат игры: {current_date} вы достигли длины в '
            f'{score} блоков.\n'
        )
    snake.reset()


def handle_keys(game_object):
    """
    Обрабатываем нажатие клавиш на клавиатуре, и защищаем от поворота на
    180 градусов и проигрыша.
    ESC - выход из игры
    N - начать новую игру
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pg.K_n:
                main()
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit


def main():
    """Основное тело игры"""
    # Инициализация pg:
    pg.init()
    # Создаём объекты и заливаем фон нужным цветом
    snake = Snake()
    apple = Apple(snake)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        snake.update_direction()
        snake.move()

        # Проверка столкновения с яблоком.
        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position()

        # Проверка столкновения с собой.
        elif snake.get_head_position() in snake.positions[1:]:
            end_game(len(snake.positions), snake)
            apple.randomize_position()
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
