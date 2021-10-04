from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Union, Any
from .common import Stats


class Item(metaclass=ABCMeta):
    def __init__(self, item_name, flavor_text):
        self.name = item_name
        self.flavor_text = flavor_text
        self.equipped = False

    @abstractmethod
    def __eq__(self, other: Any): ...

    @abstractmethod
    def on_use(self, *args: Any): ...


class Weapon(Item):
    def __init__(self, weapon_name: str, flavor_text: str, stats: Stats):
        super().__init__(weapon_name, flavor_text)
        self.stats = stats

    def on_use(self): ...

    def __eq__(self, other: Union[str, Weapon]):
        if isinstance(other, Weapon):
            return other.name == self.name
        return self.name == other


class Armor(Item):
    def __init__(self, armor_name: str, flavor_text: str, piece_type: int,  stats: Stats):
        super().__init__(armor_name, flavor_text)
        self.piece_type = piece_type
        self.stats = stats

    def __eq__(self, other: Union[str, Consumable]):
        if isinstance(other, Weapon):
            return other.name == self.name
        return self.name == other

    def on_use(self): ...


class Consumable(Item):
    def __eq__(self, other: Union[str, Consumable]):
        if isinstance(other, Weapon):
            return other.name == self.name
        return self.name == other

    def on_use(self): ...
