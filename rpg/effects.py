from abc import ABCMeta, abstractmethod
from typing import Optional, Callable, List, Tuple

from .characters import Character, Stats


class Effect(metaclass=ABCMeta):
    def __init__(self, effect_name: str, effect_desc: str,
                 duration: int):
        self.name = effect_name
        self.desc = effect_desc
        self.duration = duration

    @abstractmethod
    def modify(self, character: Character) -> Optional[str]: ...


class EffectiveStatsMod(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int,
                 modify_func: Callable[[Character], str]):
        super().__init__(effect_name, effect_desc, duration)
        self.modify_func = modify_func

    def modify(self, character: Character) -> Optional[str]:
        if self.duration:
            self.duration -= 1
            return self.modify_func(character)


class DummyEffect(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int,
                 text_func: Callable[[Character], str]):
        super().__init__(effect_name, effect_desc, duration)
        self.text_func = text_func

    def modify(self, character: Character) -> Optional[str]:
        if self.duration:
            self.duration -= 1
            return self.text_func(character)


class TurnSkip(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int,
                 text_func: Callable[[Character], str]):
        super().__init__(effect_name, effect_desc, duration)
        self.text_func = text_func

    def modify(self, character: Character) -> Optional[str]:
        if self.duration:
            self.duration -= 1
            return self.text_func(character)


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


class SkillReplaceEffect(Effect):
    def __init__(self, effect_name: str, effect_desc: str, duration: int,
                 skill):
        super().__init__(effect_name, effect_desc, duration)
        self.cached_skills: Optional[List[Skill]] = None
        self.skill = skill

    def modify(self, character: Character) -> Optional[str]:
        if self.cached_skills is None:
            self.cached_skills = character.skills
            character.skills = [self.skill] * len(self.cached_skills)

        if self.duration:
            self.duration -= 1
            if self.duration == 0:
                character.skills = self.cached_skills
            return
