from __future__ import annotations

from .characters import Character, Player

from typing import List, Tuple, Callable, Union, Optional


class Script:
    def __init__(self):
        self.protagonists: List[Player] = []
        self.story: List[Union[Dialogue, Choice]] = []

    def add_protagonist(self, protagonist: Player):
        self.protagonists.append(protagonist)

    def add_dialogue(self, dialogue: Dialogue):
        self.story.append(dialogue)

    def add_choice(self, choice: Choice):
        self.story.append(choice)

    def __iter__(self):
        return iter(self.story)

    def __next__(self):
        return next(self)


class Dialogue:
    def __init__(self, lines: Optional[List[Tuple[Character, str]]] = None):
        self.lines: List[Tuple[Character, str]] = lines or []

    def add_line(self, author: Character, line: str):
        self.lines.append((author, line))

    def __len__(self):
        return len(self.lines)

    def __iter__(self):
        return iter(self.lines)

    def __next__(self):
        return next(self)

    def __getitem__(self, index: int) -> Tuple[Character, str]:
        return self.lines[index]


class Choice:
    def __init__(self):
        self.dialogues: List[Tuple[str, Dialogue]] = []

    def __iter__(self):
        return iter(self.dialogues)

    def __next__(self):
        return next(self)

    def __len__(self):
        return len(self.dialogues)

    def __getitem__(self, index: int):
        return self.dialogues[index]

    def add_choice(self, choice: str, dialogue: Dialogue):
        self.dialogues.append((choice, dialogue))

    def select(self, choice: str):
        return next((dialogue for dialogue in self.dialogues if dialogue[0] == choice), None)
