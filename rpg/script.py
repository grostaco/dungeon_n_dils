from __future__ import annotations

from typing import List, Tuple, Union, Optional, Iterable, Literal
from itertools import cycle, chain

from .characters import Character
from operator import attrgetter
from .util import as_gen


class Script:
    def __init__(self):
        self.protagonists: List[Character] = []
        self.story: List[Union[Dialogue, Choice]] = []

    def add_protagonist(self, protagonist: Character):
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


class Fight:
    def __init__(self, left: Iterable[Character], right: Iterable[Character]):
        self.left = list(left)
        self.right = list(right)
        self.lookup = tuple(chain.from_iterable([left, right]))
        self.name_lookup = {character.name: character for character in self.lookup}
        self.turns = cycle(self.lookup)
        self.current: Optional[Character] = None

    def next_turn(self) -> Optional[Character]:
        if not any(map(attrgetter('effective_stats.hp'), self.left)) or not any(map(attrgetter('effective_stats.hp'), self.right)):
            return None

        # health being negative is intentional
        if self.current:
            self.update_effect(self.current)
        self.current = next((turn for turn in self.turns if turn.effective_stats.hp), None)
        if self.current is None:
            raise RuntimeError('Every character has 0 hp which is impossible to reach here.')

        return self.current

    # should only be called if next_turn returns None
    def winner(self) -> Union[Literal['left'], Literal['right'], None]:
        if not any(map(attrgetter('effective_stats.hp'), self.left)):
            return 'left'
        elif not any(map(attrgetter('effective_stats.hp'), self.right)):
            return 'right'
        return None

    def turn_action(self, skill_name: str, target_names: Optional[str, List[str]]):
        skill = next((skill for skill in self.current.skills if skill.name == skill_name), None)
        targets = (self.name_lookup[target] for target in as_gen([target_names]))
        if not skill:
            raise ValueError(f'Skill name {skill_name} does not exist for character {self.current.name}')
        if isinstance(target_names, str):
            targets = next(targets, None)
        elif target_names is None:
            targets = None

        skill.use(self.current, targets)

    @staticmethod
    def update_effect(character: Character):
        for effect in character.effects:
            effect.modify(character)
