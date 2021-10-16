from __future__ import annotations

from typing import List, Tuple, Union, Optional, Iterable, Literal, TYPE_CHECKING
from itertools import cycle, chain
import queue

from .characters import Character
from operator import attrgetter
from .util import as_gen

from .effects import *


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
    def __init__(self, dialogues: Optional[List[Tuple[str, Dialogue]]] = None):
        self.dialogues: List[Tuple[str, Dialogue]] = dialogues or []

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
        self.effect_queue = queue.Queue()

    def next_turn(self) -> Optional[Character]:
        if not any(map(attrgetter('effective_stats.hp'), self.left)) or not any(
                map(attrgetter('effective_stats.hp'), self.right)):
            return None

        # health being negative is intentional
        if self.current:
            self.update_effect(self.current)

        while current := next(turn for turn in self.turns if turn.effective_stats.hp):
            self.current = current
            if any(isinstance(effect, Paralysis) for effect in current.effects):
                self.update_effect(self.current)
            else:
                break

        return self.current

    # should only be called if next_turn returns None
    def winner(self) -> Union[Literal['left'], Literal['right'], None]:
        if not any(map(attrgetter('effective_stats.hp'), self.left)):
            return 'left'
        elif not any(map(attrgetter('effective_stats.hp'), self.right)):
            return 'right'
        return None

    def turn_action(self, skill_name: str, target_names: Optional[str, List[str]]) -> str:
        skill = next((skill for skill in self.current.skills if skill.name == skill_name), None)
        targets = (self.name_lookup[target] for target in as_gen([target_names]))
        if not skill:
            raise ValueError(f'Skill name {skill_name} does not exist for character {self.current.name}')

        if target_names is None:
            targets = None
        else:
            targets = next(targets, None)

        stat_modifiers = [effect for effect in self.current.effects if isinstance(effect, StatsMod)]
        old_stats = self.current.effective_stats
        for stat_modifier in stat_modifiers:
            self.current.effective_stats = stat_modifier.trigger(self.current)

        skill.use(self.current, targets)
        use_text = skill.use_text(self.current, targets)
        self.current.effective_stats = old_stats
        return use_text

    def update_effect(self, character: Character):
        for effect in character.effects:
            e = effect.modify(character)
            if e:
                self.effect_queue.put_nowait(e)

            if effect.duration == 0:
                character.effects.remove(effect)
