from __future__ import annotations

from abc import ABCMeta
from typing import Optional, List, Iterable

from .common import Stats
from .items import Weapon, Armor, Consumable


class Character(metaclass=ABCMeta):
    def __init__(self, name: str,
                 weapons: Iterable[Weapon] = (), armors: Iterable[Armor] = (), consumables: Iterable[Consumable] = (),
                 stats: Stats = None):
        self.name = name
        self.weapons = weapons
        self.consumables = consumables
        self.armors = armors
        self.stats = stats
        self.equipped_weapon = Weapon('Baby bitch hands', 'Your pussy ass hands', Stats())
        self.equipped_armors: List[Optional[Armor]] = [Armor('Nothing', 'Stop being poor', 1, Stats()), None, None]


class Player(Character):
    def __init__(self, name, weapons, consumables, armors, stats):
        super().__init__(name, weapons, armors, consumables, stats)

    def equip_weapon(self, weapon_name: str) -> Optional[Weapon]:
        weapon = tuple(filter(lambda w: w.name == weapon_name, self.weapons))
        if weapon and weapon[0] is not self.equipped_weapon:
            self.unequip_weapon()
            self.equipped_weapon = weapon[0]
            self.equipped_weapon.name += ' *(Equipped)*'
            return weapon[0]
        return None

    def equip_armor(self, armor_name: str) -> Optional[Armor]:
        armor = tuple(filter(lambda a: a.name == armor_name, self.armors))
        if armor:
            self.unequip_armor(armor[0].name)
            self.equipped_armors[armor[0].piece_type] = armor[0]
            self.equipped_armors[armor[0].piece_type].name += ' *(Equipped)*'
            return armor[0]
        return None

    def get_item_stats(self) -> Stats:
        return self.equipped_weapon.stats + sum([armor.stats for armor in self.equipped_armors])

    def unequip_weapon(self) -> None:
        if self.equipped_weapon:
            self.equipped_weapon.name = self.equipped_weapon.name[:-len(' *(Equipped)*')]
            self.equipped_weapon = None

    def unequip_armor(self, armor_name: str) -> None:
        armor = tuple(filter(lambda a: a and a.name == armor_name, self.equipped_armors))
        if armor:
            self.equipped_armors[armor[0].piece_type].name = self.equipped_armors[armor[0].piece_type].name[
                                                             :-len(' *(Equipped)*')]
            self.equipped_armors[armor[0].piece_type] = None
