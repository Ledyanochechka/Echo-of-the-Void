import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Player(arcade.Sprite):
    def __init__(self, image_path=":resources:images/animated_characters/female_person/femalePerson_idle.png"):
        super().__init__(image_path, scale=0.5)
        self.speed = 5
        self.sprint_speed = 10
        self.jump_speed = 12
        self.physics_engine = None
        self.can_jump = False
        self.is_sprinting = False
        self.facing_right = True

    def setup_physics(self, physics_engine):
        self.physics_engine = physics_engine

    def update(self):
        super().update()
        if self.physics_engine:
            self.can_jump = self.physics_engine.can_jump()

        if self.change_x > 0:
            self.scale_x = abs(self.scale_x)
            self.facing_right = True
        elif self.change_x < 0:
            self.scale_x = -abs(self.scale_x)
            self.facing_right = False

        if self.left < 0:
            self.left = 0
            self.change_x = 0
        if self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
            self.change_x = 0

    def move(self, direction):
        current_speed = self.sprint_speed if self.is_sprinting else self.speed
        if direction == "right":
            self.change_x = current_speed
        elif direction == "left":
            self.change_x = -current_speed

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
            self.change_x = abs(self.change_x) / self.change_x * current_speed


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Player Example")
        self.scene = None
        self.player = None
        self.physics_engine = None
        self.left_pressed = False
        self.right_pressed = False
        self.shift_pressed = False

    def setup(self):
        self.scene = arcade.Scene()
        self.player = Player()
        self.player.center_x = 400
        self.player.center_y = 100
        self.scene.add_sprite("Player", self.player)

        platforms = arcade.SpriteList()
        for x in range(0, 900, 64):
            platform = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            platform.center_x = x
            platform.center_y = 32
            platforms.append(platform)

        platform1 = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
        platform1.center_x = 300
        platform1.center_y = 200
        platforms.append(platform1)

        self.scene.add_sprite_list("Platforms", sprite_list=platforms)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=0.5,
            walls=self.scene["Platforms"]
        )
        self.player.setup_physics(self.physics_engine)

    def on_draw(self):
        self.clear()
        self.scene.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()

        if self.left_pressed and not self.right_pressed:
            self.player.move("left")
        elif self.right_pressed and not self.left_pressed:
            self.player.move("right")
        else:
            self.player.stop()

        self.player.sprint(self.shift_pressed)
        self.player.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            self.player.jump()
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = False


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
