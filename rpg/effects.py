from abc import ABCMeta, abstractmethod
from typing import Optional, Callable

from .characters import Character, Stats


class Effect(metaclass=ABCMeta):
    def __init__(self, effect_name: str, effect_desc: str,
                 duration: int):
        self.name = effect_name
        self.desc = effect_desc
        self.duration = duration

    @abstractmethod
    def modify(self, character: Character) -> Optional[str]: ...


# Take 5% off of the character's health pool
class Poison(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int):
        super().__init__(effect_name, effect_desc, duration)

    def modify(self, character: Character) -> Optional[str]:
        if self.duration:
            character.effective_stats.hp = max(0, character.effective_stats.hp - character.stats.hp * 0.05)
            self.duration -= 1
            return f'**{character.name}** took `{character.stats.hp * 0.15}` dmg from **canser**'


class Paralysis(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int):
        super().__init__(effect_name, effect_desc, duration)

    def modify(self, character: Character) -> Optional[str]:
        if self.duration:
            self.duration -= 1
            return f'**{character.name}** couldn\'t move due to paralysis'


class StatsMod(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int,
                 modify_func: Callable[[Character], Stats],
                 modify_text_func: Callable[[Character], str]):
        super().__init__(effect_name, effect_desc, duration)
        self.modify_func = modify_func
        self.modify_text_func = modify_text_func

    def modify(self, character: Character) -> Optional[str]:
        if self.duration:
            self.duration -= 1
            return self.modify_text_func(character)

    def trigger(self, character: Character):
        return self.modify_func(character)

