import arcade

from constants import WORLD_WIDTH


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
        self.is_alive = True
        self.is_won = False

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

            direction = 1 if self.change_x > 0 else -1
            self.change_x = direction * current_speed

    def die(self):
        self.is_alive = False
        self.change_x = 0
        self.change_y = 0