from abc import ABCMeta, abstractmethod
from typing import Optional, List, Iterable
from .items import Item, Weapon, Armor, Consumable


class Stats:
    def __init__(self, hp: float,
                 defense: float,
                 atk: float,
                 intelligence: float,
                 ):
        self.hp = hp
        self.defense = defense
        self.atk = atk
        self.int = intelligence


class Character(metaclass=ABCMeta):
    def __init__(self, name: str,
                 weapons: Iterable[Weapon] = (), armors: Iterable[Armor] = (), consumables: Iterable[Consumable] = (),
                 stats: Stats = None):
        self.name = name
        self.weapons = weapons
        self.consumables = consumables
        self.armors = armors
        self.stats = stats
        self.equipped_weapon: Optional[Weapon] = None
        self.equipped_armors: Optional[List[Optional[Armor]]] = None


class Player(Character):
    def __init__(self, name, weapons, consumables, armors, stats):
        super().__init__(name, weapons, armors, consumables, stats)

    def equip_weapon(self, weapon_name: str) -> Optional[Weapon]:
        weapon = tuple(filter(lambda w: w.name == weapon_name, self.weapons))
        if weapon:
            self.equipped_weapon = weapon[0]
            return weapon[0]
        return None

    def equip_armor(self, armor_name: str) -> Optional[Armor]:
        armor = tuple(filter(lambda a: a.name == armor_name, self.armors))
        if armor:
            self.equipped_armors[armor[0].piece_type] = armor[0]
            return armor[0]
        return None

    def unequip_weapon(self) -> None:
        self.equipped_weapon = None

    def unequip_armor(self, idx: int) -> None:
        self.equipped_armors[idx] = None



