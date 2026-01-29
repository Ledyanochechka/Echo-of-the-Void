import arcade


class NPC(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("images/npc/npc.png", scale=0.8)
        self.center_x = x
        self.center_y = y
        self.dialog_active = False
        self.dialog_phrases = [
            "Приветствую странник...",
            "Ты в самом низу мира...",
            'Удачи попасть наверх...',
            'Тебе будут мешать...'
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