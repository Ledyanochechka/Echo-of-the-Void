import arcade


class Platform(arcade.Sprite):
    def __init__(self, x, y, width=100, height=20):

        super().__init__("images/backgrounds/island.png", scale=1.0)
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.change_x = 0
        self.change_y = 0
