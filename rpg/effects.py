from abc import ABCMeta, abstractmethod


class Effect(metaclass=ABCMeta):
    def __init__(self, effect_name: str, effect_desc: str):
        self.name = effect_name
        self.desc = effect_desc

    @abstractmethod
    def modify(self, *args): ...


class Frozen(Effect):
    def __init__(self, effect_name: str, effect_desc: str):
        super().__init__(effect_name, effect_desc)

    def modify(self, *args): ...
