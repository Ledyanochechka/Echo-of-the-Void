import arcade
from player import Player
from room import Room
from ui_views import LoseWindow, WinWindow, PauseWindow
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT
from npc import NPC



class MyGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics_engine = None
        self.is_paused = False

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

        self.create_rooms()

        self.player = Player()
        self.player.center_x = 380
        self.player.center_y = 300
        self.scene.add_sprite("Player", self.player)



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

        self.room1 = Room(x=450, y=2700, width=600, height=5000)
        self.rooms.append(self.room1)
        self.room2 = Room(x=2000, y=2700, width=600, height=5000)
        self.rooms.append(self.room2)

        self.current_room = self.room1

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
                self.window.show_view(LoseWindow())
                self.game_over = True
                break

            # Проверяем столкновение игрока с пулями в комнате
            bullet_collision = arcade.check_for_collision_with_list(self.player, room.bullets)
            if bullet_collision:
                print("loose - попал под обстрел")
                # Удаляем пулю, в которую попал игрок
                for bullet in bullet_collision:
                    bullet.remove_from_sprite_lists()

                self.player.die()
                self.window.show_view(LoseWindow())
                self.game_over = True
                break

    def on_draw(self):
        self.clear()

        if self.is_paused:
            self.ui_camera.use()

            self.pause_text.x = self.window.width // 2
            self.pause_text.y = self.window.height // 2 + self.pause_text.content_height // 2

            self.pause_batch.draw()

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
            self.game_over_text.draw()

    def on_update(self, delta_time):
        if not self.physics_engine or self.game_over or self.is_paused:
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

        if self.current_room == self.room1:
            if self.player.center_x in [i for i in range(375, 425)] and self.player.center_y in [i for i in range(200, 250)]:
                self.player.center_x = 2025
                self.player.center_y = 5200
        elif self.current_room == self.room2:
            if self.player.center_x in [i for i in range(1700, 2300)] and self.player.center_y in [i for i in range(5000, 5250)]:
                if self.game_over:
                    self.window.show_view(LoseWindow())
                else:
                    self.window.show_view(WinWindow())
                    #починить окно победы
                    print('победа')

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
        elif key == arcade.key.ESCAPE:
            pause = PauseWindow(self)
            self.window.show_view(pause)
            return

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = False

