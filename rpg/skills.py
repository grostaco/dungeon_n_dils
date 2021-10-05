from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Union, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .characters import Character


class Skill(metaclass=ABCMeta):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def use(self, user: Character, targets: Union[Character, Iterable[Character], None]): ...


# Scales off of the user's ATK stats
class NormalAttack(Skill):
    def __init__(self):
        super().__init__('Normal Attack')

    def use(self, user: Character, target: Character):
        target.effective_stats.hp -= min(target.effective_stats.hp, 10 + user.effective_stats.atk * 0.4)


class Heal(Skill):
    def __init__(self):
        super().__init__('Heal')

    def use(self, user: Character, target: Character):
        target.effective_stats.hp = min(target.stats.hp,
                                        target.effective_stats.hp + 5.0 + user.effective_stats.int * 0.4)
