import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from game import MyGame
from ui_views import StartView


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Echo of the Void")
    game = MyGame()
    start = StartView(game)
    window.show_view(start)
    arcade.run()


if __name__ == "__main__":
    main()
