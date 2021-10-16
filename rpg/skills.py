from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Union, Iterable, TYPE_CHECKING

from .common import Stats
from .effects import Poison, Paralysis, StatsMod

if TYPE_CHECKING:
    from .characters import Character


class Skill(metaclass=ABCMeta):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def use(self, user: Character, targets: Union[Character, Iterable[Character], None]): ...

    @abstractmethod
    def use_text(self, user: Character, targets: Union[Character, Iterable[Character], None]) -> str: ...


# Scales off of the user's ATK stats
class NormalAttack(Skill):
    def __init__(self):
        super().__init__('Normal Attack')

    def use(self, user: Character, target: Character):
        print(user.effective_stats.atk)
        target.effective_stats.hp -= min(target.effective_stats.hp, 10 + user.effective_stats.atk * 0.4)

    def use_text(self, user: Character, target: Character) -> str:
        return f'**{user.name}** used **{user.equipped_weapon.name}** and did a normal attack and dealt ' \
               f'`{round(min(target.effective_stats.hp, 10 + user.effective_stats.atk * 0.4), 2)}` dmg to **{target.name}**'


class Heal(Skill):
    def __init__(self):
        super().__init__('Heal')

    def use(self, user: Character, target: Character):
        target.effective_stats.hp = min(target.stats.hp,
                                        target.effective_stats.hp + (
                                                target.stats.hp * 0.4) * user.effective_stats.int / 10)

    def use_text(self, user: Character, target: Character) -> str:
        return f'**{user.name}** used **{user.equipped_weapon.name}** did a heal and recovered' \
               f' `{round(min(target.stats.hp - target.effective_stats.hp, (target.stats.hp * 0.4) * user.effective_stats.int / 10), 2)}` hp ' \
               f'for **{target.name}**'


class Spit(Skill):
    def __init__(self):
        super().__init__('Spit')

    def use(self, user: Character, target: Character):
        target.effects.append(Poison('Canser', 'Corrode', 5))

    def use_text(self, user: Character, target: Character) -> str:
        return f'**{user.name}** spat on **{target.name}** and gave **{target.name}** `canser`'


class PabloSerenade(Skill):
    def __init__(self):
        super().__init__('Pablo\'s Serenade')

    def use(self, user: Character, target: Character):
        target.effects.append(StatsMod('Wet panties', '', 3,
                                       lambda character: Stats(character.effective_stats.hp,
                                                               character.effective_stats.defense,
                                                               character.effective_stats.atk * 0.40,
                                                               character.effective_stats.int),
                                       lambda character: f'{character.name}\'s panties is too wet to attack properly'))

    def use_text(self, user: Character, target: Character) -> str:
        return f'**{user.name}** sang for **{target.name}** and made **{target.name}** wet'


class PPTouch(Skill):
    def __init__(self):
        super().__init__('PP Touch')

    def use(self, user: Character, target: Character):
        target.effects.append(Paralysis('PP hard', 'Placeholder', 1))

    def use_text(self, user: Character, target: Character) -> str:
        return f'**{target.name}** dik\'s was too hard and couldn\'t move'
