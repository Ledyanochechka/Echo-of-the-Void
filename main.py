import arcade
from pyglet.graphics import Batch

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 8000
WORLD_HEIGHT = 6000


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


class Player(arcade.Sprite):
    def __init__(self, image_path="images/npc/player_good_npc.png"):
        super().__init__(image_path, scale=0.5)
        self.speed = 3
        self.sprint_speed = 5
        self.jump_speed = 12
        self.physics_engine = None
        self.can_jump = False
        self.is_sprinting = False

    def setup_physics(self, physics_engine):
        self.physics_engine = physics_engine

    def update(self):
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
        current_speed = self.sprint_speed if self.is_sprinting else self.speed
        self.change_x = current_speed if direction == "right" else -current_speed

    def stop(self):
        self.change_x = 0

    def jump(self):
        if self.can_jump and self.physics_engine:
            self.change_y = self.jump_speed
            self.can_jump = False

    def sprint(self, is_sprinting):
        self.is_sprinting = is_sprinting
        if self.change_x != 0:
            current_speed = self.sprint_speed if is_sprinting else self.speed
            self.change_x = (abs(self.change_x) / self.change_x) * current_speed


class MyGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics_engine = None

        self.left_pressed = False
        self.right_pressed = False
        self.shift_pressed = False

        self.background = None
        self.camera = None

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

        self.scene = arcade.Scene()

        self.player = Player()
        self.player.center_x = 400
        self.player.center_y = 100
        self.scene.add_sprite("Player", self.player)

        platforms = arcade.SpriteList()
        for x in range(0, 9000, 64):
            platform = arcade.Sprite("images/backgrounds/ground.png", scale=0.5)
            platform.center_x = x
            platform.center_y = 32
            platforms.append(platform)

        for i in range(10):
            platform1 = arcade.Sprite("images/backgrounds/island.png", scale=0.5)
            platform1.center_x = 300 + i * 100
            platform1.center_y = 200 + i * 100
            platforms.append(platform1)

        self.scene.add_sprite_list("Platforms", sprite_list=platforms)

        enemies = arcade.SpriteList()
        enemy = arcade.Sprite(':resources:images/tiles/mushroomRed.png')
        enemy.center_x = 600
        enemy.center_y = 300
        enemies.append(enemy)

        self.scene.add_sprite_list('Enemies', sprite_list=enemies)

        final_flag = arcade.Sprite(':resources:images/items/flagRed2.png', scale=0.5)
        final_flag.center_x = 700
        final_flag.center_y = 72

        self.scene.add_sprite('Final_flag', final_flag)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=0.5, walls=self.scene["Platforms"]
        )
        self.player.setup_physics(self.physics_engine)

    def on_draw(self):
        self.clear()

        for i in range(10):
            for j in range(10):
                arcade.draw_texture_rect(
                    self.background,
                    arcade.rect.XYWH(0 + SCREEN_WIDTH * j, 0 + SCREEN_HEIGHT * i, SCREEN_WIDTH, SCREEN_HEIGHT),
                )

        self.camera.use()
        self.scene.draw()

    def on_update(self, delta_time):
        if not self.physics_engine:
            return

        self.physics_engine.update()

        if self.left_pressed and not self.right_pressed:
            self.player.move("left")
        elif self.right_pressed and not self.left_pressed:
            self.player.move("right")
        else:
            self.player.stop()

        if self.player.center_x in [i for i in range(650, 700)] and self.player.center_y in [i for i in range(0, 100)]:
            print('win')

        self.player.sprint(self.shift_pressed)
        self.player.update()
        self.center_camera_to_player()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.player.jump()
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = True

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
