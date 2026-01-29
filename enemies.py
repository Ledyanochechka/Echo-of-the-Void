import arcade
import math
import random


class Bullet(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y, speed=5):
        texture = arcade.make_circle_texture(10, arcade.color.YELLOW)
        super().__init__(texture)

        self.center_x = x
        self.center_y = y

        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)

        self.change_x = dx / dist * speed if dist else 0
        self.change_y = dy / dist * speed if dist else 0
        self.lifetime = 180

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.lifetime -= 1
        return self.lifetime <= 0


class Enemy(arcade.Sprite):
    def __init__(self, x, y, is_shooter=False):
        # Создаем врага
        color = arcade.color.ORANGE if is_shooter else arcade.color.RED
        texture = arcade.make_soft_square_texture(40, color)
        super().__init__(texture, scale=0.8)

        self.center_x = x
        self.center_y = y
        self.speed = 1.5
        self.direction = 1  # 1 для движения вправо, -1 для движения влево
        self.change_x = self.speed * self.direction

        # Для патрулирования (движение вперед-назад)
        self.patrol_distance = 100
        self.start_x = x
        self.max_x = x + self.patrol_distance
        self.min_x = x - self.patrol_distance

        # Для стрельбы
        self.is_shooter = is_shooter
        self.shoot_timer = random.uniform(0, 2)  # Случайное начальное значение таймера
        self.shoot_cooldown = 2.0  # Время между выстрелами в секундах
        self.bullet_speed = 4
        self.shoot_range = 400  # Максимальная дистанция стрельбы

        # Для врагов на стенах/потолке
        self.is_on_wall = False
        self.is_on_ceiling = False

    def update_shooting(self, delta_time, player_x, player_y):
        if not self.is_shooter:
            return False

        self.shoot_timer += delta_time

        # Проверяем расстояние до игрока
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Если игрок в пределах дальности стрельбы и прошло достаточно времени
        if distance <= self.shoot_range and self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            return True

        return False

    def get_shoot_direction(self, player_x, player_y):
        """Возвращает направление выстрела к игроку"""
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            return dx / distance, dy / distance
        return 1, 0  # По умолчанию стреляем вправо