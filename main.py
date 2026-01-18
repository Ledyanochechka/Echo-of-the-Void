import arcade
from pyglet.graphics import Batch
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 8000
WORLD_HEIGHT = 6000


class Platform(arcade.Sprite):
    def __init__(self, x, y, width=100, height=20):

        super().__init__("images/backgrounds/island.png", scale=1.0)
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.change_x = 0
        self.change_y = 0


class Bullet(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y, speed=5):

        texture = arcade.make_circle_texture(10, arcade.color.YELLOW)
        super().__init__(texture, scale=1.0)

        self.center_x = x
        self.center_y = y
        self.speed = speed

        # Рассчитываем направление к цели
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            self.change_x = (dx / distance) * speed
            self.change_y = (dy / distance) * speed
        else:
            self.change_x = 0
            self.change_y = 0

        # Время жизни пули (в кадрах)
        self.lifetime = 180  # 3 секунды при 60 FPS

    def update(self):
        """Обновляет позицию пули и уменьшает время жизни"""
        super().update()

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
        first_x = random.uniform(self.left + 100, self.right - 100)
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


class StartView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.batch = Batch()
        self.txt = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.batch = Batch()
        self.txt = arcade.Text(
            "Нажмите ENTER для начала игры",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.YELLOW_ORANGE,
            25,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch,
        )

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.game_view.setup()
            self.window.show_view(self.game_view)


class NPC(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(":resources:images/tiles/mushroomRed.png", scale=0.8)
        self.center_x = x
        self.center_y = y
        self.dialog_active = False
        self.dialog_phrases = [
            "Привет! Я NPC.",
            "test"
        ]
        self.current_phrase_index = 0
        self.dialog_sprite = None

    def interact(self):
        if not self.dialog_active:
            # Начинаем диалог с первой фразы
            self.dialog_active = True
            self.current_phrase_index = 0
            self.dialog_sprite.center_x = self.center_x
            self.dialog_sprite.center_y = self.center_y + 120
        else:
            self.current_phrase_index += 1

            # Если фразы закончились, закрываем диалог
            if self.current_phrase_index >= len(self.dialog_phrases):
                self.dialog_active = False
                self.current_phrase_index = 0
                self.dialog_sprite = None

    def get_current_phrase(self):
        if self.current_phrase_index < len(self.dialog_phrases):
            return self.dialog_phrases[self.current_phrase_index]
        return ""

    def get_progress_text(self):
        return f"{self.current_phrase_index + 1}/{len(self.dialog_phrases)}"

    def draw_dialog(self):
        if not self.dialog_active:
            return

        # Рисуем текст диалога рядом с уменьшенной текстурой
        text_x = self.center_x + 60
        text_y = self.center_y + 120

        # Текст текущей фразы
        current_phrase = self.get_current_phrase()
        arcade.draw_text(
            current_phrase,
            text_x, text_y,
            arcade.color.BLACK, 12,
            anchor_x="center", anchor_y="center",
            width=180, align="center"
        )

        # Проверяем колличество сказанных фраз
        progress_text = self.get_progress_text()
        arcade.draw_text(
            progress_text,
            text_x, text_y - 20,
            arcade.color.DARK_GRAY, 10,
            anchor_x="center", anchor_y="center"
        )

        # Подсказка для переключения/закрытия
        if self.current_phrase_index < len(self.dialog_phrases) - 1:
            hint_text = "Нажмите E для продолжения"
        else:
            hint_text = "Нажмите E для завершения"

        arcade.draw_text(
            hint_text,
            text_x, text_y + 30,
            arcade.color.DARK_GREEN, 10,
            anchor_x="center", anchor_y="center"
        )


class Player(arcade.Sprite):
    def __init__(self, image_path="images/npc/player_good_npc.png"):

        try:
            super().__init__(image_path, scale=0.5)
        except FileNotFoundError:

            texture = arcade.make_soft_square_texture(50, arcade.color.BLUE)
            super().__init__(texture, scale=0.5)

        self.speed = 3
        self.sprint_speed = 5
        self.jump_speed = 12
        self.physics_engine = None
        self.can_jump = False
        self.is_sprinting = False
        self.is_alive = True  # Добавляем флаг жизни игрока

    def setup_physics(self, physics_engine):
        self.physics_engine = physics_engine

    def update(self):
        if not self.is_alive:
            return


        super().update()
        if self.physics_engine:
            self.can_jump = self.physics_engine.can_jump()

        if self.change_x > 0:
            self.scale_x = abs(self.scale_x)
        elif self.change_x < 0:
            self.scale_x = -abs(self.scale_x)

        if self.left < 0:
            self.left = 0
            self.change_x = 0
        if self.right > WORLD_WIDTH:
            self.right = WORLD_WIDTH
            self.change_x = 0

    def move(self, direction):
        if not self.is_alive:
            return

        current_speed = self.sprint_speed if self.is_sprinting else self.speed
        if direction == "right":
            self.change_x = current_speed
        elif direction == "left":
            self.change_x = -current_speed

    def stop(self):
        if not self.is_alive:
            return
        self.change_x = 0

    def jump(self):
        if not self.is_alive:
            return

        if self.can_jump and self.physics_engine:
            self.change_y = self.jump_speed
            self.can_jump = False

    def sprint(self, is_sprinting):
        if not self.is_alive:
            return

        self.is_sprinting = is_sprinting
        if self.change_x != 0:
            current_speed = self.sprint_speed if is_sprinting else self.speed
            # Безопасно изменяем скорость, сохраняя направление
            direction = 1 if self.change_x > 0 else -1
            self.change_x = direction * current_speed

    def die(self):
        self.is_alive = False
        self.change_x = 0
        self.change_y = 0


class MyGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics_engine = None

        self.npcs = None
        self.near_npc = None

        self.left_pressed = False
        self.right_pressed = False
        self.shift_pressed = False

        self.background = None
        self.camera = None

        self.game_over = False
        self.game_over_text = None

        # Добавляем комнаты
        self.rooms = []
        self.current_room = None

    def center_camera_to_player(self):
        cam_x, cam_y = self.camera.position
        px, py = self.player.center_x, self.player.center_y

        half_w = self.camera.viewport_width / 2
        half_h = self.camera.viewport_height / 2

        DEAD_X = 200
        DEAD_Y = 120

        left = cam_x - half_w + DEAD_X
        right = cam_x + half_w - DEAD_X
        bottom = cam_y - half_h + DEAD_Y
        top = cam_y + half_h - DEAD_Y

        if px < left:
            cam_x -= (left - px)
        elif px > right:
            cam_x += (px - right)

        if py < bottom:
            cam_y -= (bottom - py)
        elif py > top:
            cam_y += (py - top)

        cam_x = max(half_w, min(cam_x, WORLD_WIDTH - half_w))
        cam_y = max(half_h, min(cam_y, WORLD_HEIGHT - half_h))

        self.camera.position = (cam_x, cam_y)

    def setup(self):
        self.background = arcade.load_texture("images/backgrounds/background.png")

        self.camera = arcade.Camera2D()

        self.game_over = False
        self.game_over_text = None

        self.scene = arcade.Scene()

        self.player = Player()
        self.player.center_x = 400
        self.player.center_y = 300
        self.scene.add_sprite("Player", self.player)

        self.create_rooms()

        self.npcs = arcade.SpriteList()
        if self.rooms:
            npc = NPC(600, 300)
            self.npcs.append(npc)
            self.scene.add_sprite_list("NPCs", sprite_list=self.npcs)


        all_walls = arcade.SpriteList()
        for room in self.rooms:
            all_walls.extend(room.get_collision_sprites())

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=0.5, walls=all_walls
        )
        self.player.setup_physics(self.physics_engine)

        self.near_npc = None

    def create_rooms(self):
        self.rooms = []

        room1 = Room(x=450, y=2700, width=600, height=5000)
        self.rooms.append(room1)

        self.current_room = room1

    def check_npc_proximity(self):
        self.near_npc = None
        for npc in self.npcs:
            distance_x = abs(npc.center_x - self.player.center_x)
            distance_y = abs(npc.center_y - self.player.center_y)

            # Если игрок находится в радиусе 100 пикселей от NPC
            if distance_x < 100 and distance_y < 100:
                self.near_npc = npc
                break

    def check_collisions(self):
        if not self.player.is_alive or self.game_over:
            return

        for room in self.rooms:

            collision_list = arcade.check_for_collision_with_list(self.player, room.enemies)
            if collision_list:
                print("loose - столкнулся с врагом")
                self.player.die()
                self.game_over = True
                self.game_over_text = arcade.Text(
                    "ВЫ ПРОИГРАЛИ!",
                    self.window.width / 2,
                    self.window.height / 2,
                    arcade.color.RED,
                    40,
                    anchor_x="center",
                    anchor_y="center"
                )
                break

            # Проверяем столкновение игрока с пулями в комнате
            bullet_collision = arcade.check_for_collision_with_list(self.player, room.bullets)
            if bullet_collision:
                print("loose - попал под обстрел")
                # Удаляем пулю, в которую попал игрок
                for bullet in bullet_collision:
                    bullet.remove_from_sprite_lists()

                self.player.die()
                self.game_over = True
                self.game_over_text = arcade.Text(
                    "ВЫ ПРОИГРАЛИ!",
                    self.window.width / 2,
                    self.window.height / 2,
                    arcade.color.RED,
                    40,
                    anchor_x="center",
                    anchor_y="center"
                )
                break

    def on_draw(self):
        self.clear()

        # Фон
        for i in range(10):
            for j in range(10):
                arcade.draw_texture_rect(
                    self.background,
                    arcade.rect.XYWH(0 + SCREEN_WIDTH * j, 0 + SCREEN_HEIGHT * i, SCREEN_WIDTH, SCREEN_HEIGHT),
                )

        self.camera.use()

        # Рисуем все комнаты
        for room in self.rooms:
            room.draw()

        # Рисуем сцену (игрока, NPC и др.)
        self.scene.draw()

        # Рисуем диалоги всех NPC
        for npc in self.npcs:
            npc.draw_dialog()

        # Рисуем подсказку для взаимодействия, если игрок рядом с NPC
        if self.near_npc and not self.near_npc.dialog_active and self.player.is_alive:
            arcade.draw_text(
                "Нажмите E для разговора",
                self.player.center_x,
                self.player.center_y + 50,
                arcade.color.WHITE, 12,
                anchor_x="center",
                anchor_y="center"
            )

        # Если игра окончена, рисуем текст проигрыша
        if self.game_over and self.game_over_text:
            print('lost')
            self.game_over_text.draw()

    def on_update(self, delta_time):
        if not self.physics_engine or self.game_over:
            return

        self.physics_engine.update()

        # Проверяем близость к NPC
        self.check_npc_proximity()

        # Проверяем столкновения с врагами и пулями
        self.check_collisions()

        # Обновляем врагов и их стрельбу
        for room in self.rooms:
            room.update_enemies(delta_time, self.player.center_x, self.player.center_y)
            room.update_bullets()

        if self.player.is_alive:
            if self.left_pressed and not self.right_pressed:
                self.player.move("left")
            elif self.right_pressed and not self.left_pressed:
                self.player.move("right")
            else:
                self.player.stop()

            self.player.sprint(self.shift_pressed)
            self.player.update()

        # Определяем, в какой комнате находится игрок
        for room in self.rooms:
            if room.contains_point(self.player.center_x, self.player.center_y):
                self.current_room = room
                break

        self.center_camera_to_player()

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.ENTER:
                # Перезапуск игры
                self.setup()
            return

        if key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.player.jump()
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = True
        elif key == arcade.key.E and self.near_npc:
            self.near_npc.interact()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = False


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Echo of the Void")
    game_view = MyGame()
    start_view = StartView(game_view)
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()