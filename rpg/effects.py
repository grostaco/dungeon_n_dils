from abc import ABCMeta, abstractmethod
from typing import Callable, Optional


from .characters import Character
"""
On Effects

Is it [periodic] or [persistent]? If not, how does it [trigger]?
What does it [do]?

If duration is -1, it is persistent, else it is periodic
"""


class Effect(metaclass=ABCMeta):
    def __init__(self, effect_name: str, effect_desc: str,
                 duration: int, trigger: Optional[Callable]):
        self.name = effect_name
        self.desc = effect_desc
        self.duration = duration
        self.trigger = trigger

    @abstractmethod
    def modify(self, character: Character): ...


# Take 5% off of the character's health pool
class Poison(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int):
        super().__init__(effect_name, effect_desc, duration, None)

    def modify(self, character: Character):
        if self.duration:
            self.duration -= 1

