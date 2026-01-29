import arcade
import math
import random

from game_platform import Platform
from enemies import Enemy, Bullet


class Room:
    def __init__(self, x, y, width, height, wall_thickness=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.wall_thickness = wall_thickness

        # Границы комнаты
        self.left = x - width // 2
        self.right = x + width // 2
        self.bottom = y - height // 2
        self.top = y + height // 2

        # Списки для хранения спрайтов
        self.walls = arcade.SpriteList()
        self.floors = arcade.SpriteList()
        self.ceilings = arcade.SpriteList()
        self.platforms = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()

        self.load_textures()
        self.build_room()
        self.generate_platforms_improved()


        self.generate_enemies()

        self.obstacles = arcade.SpriteList()
        self.obstacles.extend(self.walls)
        self.obstacles.extend(self.ceilings)
        self.obstacles.extend(self.platforms)

        self.first_platform_x = None
        self.first_platform_y = None

    def load_textures(self):
        self.wall_texture = arcade.load_texture("images/backgrounds/wall.png")
        self.floor_texture = arcade.load_texture("images/backgrounds/floor.png")
        self.ground_texture = arcade.load_texture("images/backgrounds/ground.png")


    def build_room(self):
        wall_tile_height = 100  # Высота одной плитки текстуры
        num_tiles = math.ceil((self.height + 2 * self.wall_thickness) / wall_tile_height)

        for i in range(num_tiles):
            wall_sprite = arcade.Sprite()
            wall_sprite.texture = self.wall_texture
            wall_sprite.center_x = self.left - self.wall_thickness // 2
            wall_sprite.center_y = (self.bottom - self.wall_thickness) + (i * wall_tile_height) + (
                        wall_tile_height // 2)
            wall_sprite.width = self.wall_thickness
            wall_sprite.height = min(wall_tile_height,
                                     (self.height + 2 * self.wall_thickness) - (i * wall_tile_height))
            self.walls.append(wall_sprite)

        # Правая стена - вертикальная
        for i in range(num_tiles):
            wall_sprite = arcade.Sprite()
            wall_sprite.texture = self.wall_texture
            wall_sprite.center_x = self.right + self.wall_thickness // 2
            wall_sprite.center_y = (self.bottom - self.wall_thickness) + (i * wall_tile_height) + (
                        wall_tile_height // 2)
            wall_sprite.width = self.wall_thickness
            wall_sprite.height = min(wall_tile_height,
                                     (self.height + 2 * self.wall_thickness) - (i * wall_tile_height))
            self.walls.append(wall_sprite)

        # Пол - горизонтальный, с правильной ориентацией текстуры
        floor_tile_width = 100  # Ширина одной плитки пола
        floor_num_tiles = math.ceil((self.width + 2 * self.wall_thickness) / floor_tile_width)

        for i in range(floor_num_tiles):
            floor_sprite = arcade.Sprite()
            floor_sprite.texture = self.floor_texture
            floor_sprite.center_x = (self.left - self.wall_thickness) + (i * floor_tile_width) + (floor_tile_width // 2)
            floor_sprite.center_y = self.bottom - self.wall_thickness // 2
            floor_sprite.width = min(floor_tile_width,
                                     (self.width + 2 * self.wall_thickness) - (i * floor_tile_width))
            floor_sprite.height = self.wall_thickness
            self.walls.append(floor_sprite)  # Пол добавляется в walls, не floors

        # Потолок - горизонтальный
        for i in range(floor_num_tiles):
            ceiling_sprite = arcade.Sprite()
            ceiling_sprite.texture = self.wall_texture
            ceiling_sprite.center_x = (self.left - self.wall_thickness) + (i * floor_tile_width) + (
                        floor_tile_width // 2)
            ceiling_sprite.center_y = self.top + self.wall_thickness // 2
            ceiling_sprite.width = min(floor_tile_width,
                                       (self.width + 2 * self.wall_thickness) - (i * floor_tile_width))
            ceiling_sprite.height = self.wall_thickness
            self.ceilings.append(ceiling_sprite)

    def generate_platforms_improved(self):
        # Параметры генерации
        start_y = self.bottom + 100  # Начальная высота
        end_y = self.top - 100  # Конечная высота
        step_y = 120  # Расстояние между платформами по вертикали
        max_x_offset = 150  # Максимальное смещение по X относительно предыдущей платформы

        # Генерируем первую платформу в случайном месте внизу
        first_x = 380
        first_y = start_y
        first_platform = Platform(first_x, first_y)
        self.platforms.append(first_platform)

        # Создаем основную лестницу платформ
        current_y = first_y + step_y
        last_x = first_x

        while current_y <= end_y:
            # Генерируем случайное смещение по X относительно предыдущей платформы
            offset = random.uniform(-max_x_offset, max_x_offset)
            new_x = last_x + offset

            # Проверяем, чтобы платформа не выходила за границы комнаты
            new_x = max(self.left + 50, min(new_x, self.right - 50))

            platform = Platform(new_x, current_y)
            self.platforms.append(platform)

            last_x = new_x
            current_y += step_y

        for i in range(40): #это доп платфрмы, потому что путь из основных очень скучный
            attempts = 0
            placed = False

            while attempts < 20 and not placed:  # Ограничим попытки
                x = random.uniform(self.left + 50, self.right - 50)
                y = random.uniform(self.bottom + 100, self.top - 100)

                # Проверяем расстояние до всех существующих платформ
                too_close = False
                for existing_platform in self.platforms:
                    # Проверяем отдельно по X и Y
                    dx = abs(existing_platform.center_x - x)
                    dy = abs(existing_platform.center_y - y)

                    # Минимальные расстояния по X и Y
                    if dx < 60 and dy < 40:  # Если и по X, и по Y близко
                        too_close = True
                        break

                if not too_close:
                    platform = Platform(x, y)
                    self.platforms.append(platform)
                    placed = True

                attempts += 1

    def generate_enemies(self):
        num_enemies = random.randint(12, 25)  # От 4 до 8 врагов в комнате
        shooter_chance = 0.6  # 40% шанс что враг будет стрелком

        for _ in range(num_enemies):
            # Случайно выбираем стену: 0 - левая, 1 - правая, 2 - потолок
            wall_choice = random.randint(0, 2)

            is_shooter = random.random() < shooter_chance

            if wall_choice == 0:  # Левая стена
                x = self.left + 25  # Немного отступим от края стены
                y = random.uniform(self.bottom + 100, self.top - 100)

            elif wall_choice == 1:  # Правая стена
                x = self.right - 25  # Немного отступим от края стены
                y = random.uniform(self.bottom + 100, self.top - 100)

            else:  # Потолок
                x = random.uniform(self.left + 100, self.right - 100)
                y = self.top - 25  # Немного ниже потолка

            # Проверяем, чтобы враг не спавнился слишком близко к платформам
            too_close = False
            for platform in self.platforms:
                dx = abs(platform.center_x - x)
                dy = abs(platform.center_y - y)

                if dx < 80 and dy < 80:  # Если слишком близко к платформе
                    too_close = True
                    break

            # Также проверяем расстояние до других врагов
            for enemy in self.enemies:
                dx = abs(enemy.center_x - x)
                dy = abs(enemy.center_y - y)

                if dx < 60 and dy < 60:  # Если слишком близко к другому врагу
                    too_close = True
                    break

            if not too_close:
                enemy = Enemy(x, y, is_shooter)

                if wall_choice == 2:  # Если на потолке, двигаемся по горизонтали
                    enemy.direction = random.choice([-1, 1])
                    enemy.change_x = enemy.speed * enemy.direction
                    enemy.start_x = x
                    enemy.patrol_distance = random.randint(80, 150)
                    enemy.max_x = x + enemy.patrol_distance
                    enemy.min_x = x - enemy.patrol_distance
                    enemy.is_on_ceiling = True
                else:  # Если на стене, двигаемся по вертикали
                    enemy.direction = random.choice([-1, 1])
                    enemy.change_y = enemy.speed * enemy.direction
                    enemy.start_y = y
                    enemy.patrol_distance = random.randint(80, 150)
                    enemy.max_y = y + enemy.patrol_distance
                    enemy.min_y = y - enemy.patrol_distance
                    enemy.is_on_wall = True
                    enemy.change_x = 0  # Стенные враги двигаются только по вертикали

                self.enemies.append(enemy)

    def update_enemies(self, delta_time, player_x, player_y):
        for enemy in self.enemies:
            # Обновляем позицию врага
            enemy.center_x += enemy.change_x
            enemy.center_y += enemy.change_y

            if enemy.change_x != 0:
                if enemy.center_x >= enemy.max_x or enemy.center_x <= enemy.min_x:
                    enemy.change_x *= -1  # Меняем направление
                    enemy.direction *= -1

            if enemy.change_y != 0:
                if enemy.center_y >= enemy.max_y or enemy.center_y <= enemy.min_y:
                    enemy.change_y *= -1  # Меняем направление
                    enemy.direction *= -1

            # Проверяем, чтобы враг не выходил за пределы комнаты
            enemy.center_x = max(self.left + 30, min(enemy.center_x, self.right - 30))
            enemy.center_y = max(self.bottom + 30, min(enemy.center_y, self.top - 30))

            # Если враг стрелок, проверяем возможность выстрела
            if enemy.is_shooter:
                if enemy.update_shooting(delta_time, player_x, player_y):
                    bullet = Bullet(enemy.center_x, enemy.center_y,
                                    player_x, player_y, enemy.bullet_speed)
                    self.bullets.append(bullet)

    def update_bullets(self):
        bullets_to_remove = []

        for bullet in self.bullets:
            # Обновляем пулю
            if bullet.update():
                bullets_to_remove.append(bullet)

            # Проверяем, вышла ли пуля за пределы комнаты
            if (bullet.center_x < self.left - 50 or bullet.center_x > self.right + 50 or
                    bullet.center_y < self.bottom - 50 or bullet.center_y > self.top + 50):
                bullets_to_remove.append(bullet)

        # Удаляем старые пули
        for bullet in bullets_to_remove:
            bullet.remove_from_sprite_lists()

    def draw(self): # рисует комнату полностью
        self.walls.draw()
        self.ceilings.draw()
        self.platforms.draw()
        self.enemies.draw()
        self.bullets.draw()

    def get_collision_sprites(self):
        return self.obstacles

    def contains_point(self, x, y):
        return (self.left < x < self.right and
                self.bottom < y < self.top)

    def get_random_position(self):
        x = random.uniform(self.left + 50, self.right - 50)
        y = random.uniform(self.bottom + 50, self.top - 50)
        return x, y