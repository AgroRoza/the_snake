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

# Кнопки движения
DIRECTION_KEYS = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT
}

# Запрещённые движения
PROHIBITED_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}
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
        self.direction = RIGHT

    def update_direction(self, next_direction):
        """
        Обновляет направление перемещения змейки при нажатии на клавиши.
        Запрещает поворот на 180 градусов
        """
        if self.direction != PROHIBITED_DIRECTIONS[next_direction]:
            self.direction = next_direction

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
        """Рисуем змейку - голову и затираем последний сегмент."""
        self.draw_rect(self.positions[0])

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

    def __init__(
            self,
            occupied_cells=None,
            position=None,
            body_color=APPLE_COLOR,
    ):
        super().__init__(body_color, position)
        if occupied_cells is None:
            occupied_cells = set()
        # Позволяет передать желаемую позицию яблока при его отображении.
        self.position = position
        self.randomize_position(occupied_cells)

    def draw(self):
        """Отрисовывает яблоко - его позицию и цвета."""
        self.draw_rect()

    def randomize_position(self, occupied_cells):
        """
        При отрисовке яблока создаёт случайную позицию для него.
        Учитывает текущее положение змейки чтобя яблоко не появилось внутри.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_cells:
                break


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
    Обрабатывает нажатие клавиш на клавиатуре
    ESC - выход из игры
    N - начать новую игру
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key in DIRECTION_KEYS:
                game_object.update_direction(DIRECTION_KEYS[event.key])
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
    # Передаём в яблочко змейку, чтобы яблочко не появилось в змейке
    apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        # Проверка столкновения с яблоком.
        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        # Проверка столкновения с собой.
        elif snake.get_head_position() in snake.positions[1:]:
            end_game(len(snake.positions), snake)
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
