from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Union, Iterable, Callable, TYPE_CHECKING

from .effects import SkillReplaceEffect

if TYPE_CHECKING:
    from .characters import Character


class Skill(metaclass=ABCMeta):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def use(self, user: Character, targets: Union[Character, Iterable[Character], None]) -> str: ...


# Scales off of the user's ATK stats
class GenericSkill(Skill):
    def __init__(self, name: str, use_func: Callable[[Character, Character], str]):
        super().__init__(name)
        self.use_func = use_func

    def use(self, user: Character, target: Character):
        return self.use_func(user, target)


class DummySkill(Skill):
    def __init__(self, name: str, text_func: Callable[[Character, Character], str]):
        super().__init__(name)
        self.text_func = text_func

    def use(self, user: Character, target: Character) -> str:
        return self.text_func(user, target)


class SkillReplace(Skill):
    def __init__(self, skill_name: str, text_func: Callable[[Character, Character], str],
                 effect_name: str, skill: Skill, duration: int):
        super().__init__(skill_name)
        self.text_func = text_func
        self.replace_effect = SkillReplaceEffect(effect_name, '', duration, skill)

    def use(self, user: Character, target: Character):
        target.effects.append(self.replace_effect)
        return self.text_func(user, target)
