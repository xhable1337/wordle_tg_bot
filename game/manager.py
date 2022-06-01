from pathlib import Path
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO

from game.models import Letter, Word

path = Path(__file__).parent


class WordleManager(object):
    def __init__(self, correct_word, base_file="./assets/game.png",
                 font_file="./assets/font.ttf", font_size=72):
        self.correct_word = correct_word
        self._base_file = str(path / base_file)
        self._font_file = str(path / font_file)
        self.font_size = font_size

        # Базовые координаты (0, 0)
        self.base_x = 21
        self.base_y = 18

        # Сдвиги для блока с буквой
        self.block_x_offset = 93
        self.block_y_offset = 103

        # Сдвиги для буквы относительно блока
        self.text_x_offset = 13
        self.text_y_offset = -3

        # Счётчик слов на игровом поле
        self.word_count = 0

        # Флаг для завершения игры
        self.is_finished = False

    def __enter__(self):
        self.img = Image.open(self._base_file)
        self.draw = ImageDraw.Draw(self.img)
        self.font = ImageFont.truetype(self._font_file, self.font_size)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Удаляем img для очистки памяти
        self.img.close()

    def prepare_word(self, word: str) -> Word:
        word_obj = Word(word, [])
        for index, letter in enumerate(word):
            correct = False
            contains = False

            # Проверка на наличие буквы в слове
            if letter in self.correct_word:
                contains = True

                # Проверка на правильную позицию буквы в слове
                if letter == self.correct_word[index]:
                    correct = True

            # Добавляем объект буквы в список
            word_obj.letters.append(Letter(letter, contains, correct))

        return word_obj

    def bulk_draw_words(self, words: list[str]):
        for word in words:
            self.draw_word(self.prepare_word(word))

    def draw_word(self, word: Word):
        if self.word_count == 6:
            raise EOFError('Игровое поле уже заполнено.')

        letter_index = 0

        for letter in word.letters:
            # Открываем файл с нужным блоком для буквы
            block = Image.open(letter.block_file).convert('RGBA')

            # Вычисляем координаты блока
            block_x = self.base_x + letter_index * self.block_x_offset
            block_y = self.base_y + self.word_count * self.block_y_offset

            # Вставляем изображение блока на поле
            self.img.paste(block, (block_x, block_y), block)

            # Закрываем файл, чтобы не загружать память
            block.close()

            # Вычисляем координаты буквы относительно блока
            text_x = block_x + self.text_x_offset
            text_y = block_y + self.text_y_offset

            # Вставляем букву в блок на поле
            self.draw.text(
                xy=(text_x, text_y),
                text=letter.text.upper(),
                fill=letter.color,
                font=self.font,
            )

            letter_index += 1

        # Если получено правильное слово...
        if word.correct:
            # Вставляем рамку для выделения этого слова
            correct_word = Image.open(
                path / './assets/full_correct.png').convert('RGBA')
            self.img.paste(correct_word, (self.base_x -
                           15, block_y-15), correct_word)

            self.is_finished = True

            # Закрываем файл, чтобы не загружать память
            correct_word.close()

        self.word_count += 1

    def save(self):
        self.img.save('game-out.png')

    @property
    def image_bytes(self):
        output = BytesIO()
        self.img.save(output, format='PNG')
        output.seek(0)
        return output


word_1 = Word(
    text="НОСОК",
    letters=[
        Letter("Н", False, False),
        Letter("О", False, False),
        Letter("С", True, False),
        Letter("О", False, False),
        Letter("К", False, False),
    ]
)

word_2 = Word(
    text="САРАЙ",
    letters=[
        Letter("С", True, False),
        Letter("А", True, False),
        Letter("Р", True, True),
        Letter("А", False, False),
        Letter("Й", False, False),
    ]
)
