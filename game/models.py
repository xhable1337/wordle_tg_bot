from dataclasses import dataclass
from pathlib import Path

path = Path(__file__).parent


@dataclass
class Letter:
    text: str
    contains: bool
    correct: bool

    @property
    def color(self):
        if self.correct or self.contains:
            return (0, 0, 0)
        else:
            return (255, 255, 255)

    @property
    def block_file(self):
        if self.correct:
            return str(path / "./assets/correct.png")
        elif self.contains:
            return str(path / "./assets/contains.png")
        else:
            return str(path / "./assets/wrong.png")


@dataclass
class Word:
    text: str
    letters: list[Letter]

    @property
    def correct(self) -> bool:
        for letter in self.letters:
            if not letter.correct:
                return False

        return True
