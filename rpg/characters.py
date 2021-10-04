from __future__ import annotations

from typing import List, Iterable, TYPE_CHECKING
import copy

from .common import Stats
from .items import Weapon, Armor, Consumable

if TYPE_CHECKING:
    from .skills import Skill
    from .effects import Effect

hands = Weapon('', '', Stats())
nothing = Armor('', '', -1, Stats())


class Character:
    def __init__(self, name: str,
                 weapons: Iterable[Weapon] = (), armors: Iterable[Armor] = (), consumables: Iterable[Consumable] = (),
                 stats: Stats = None):
        self.name = name
        self.weapons = weapons
        self.consumables = consumables
        self.armors = armors
        self.stats = stats
        self.effective_stats = copy.copy(stats)
        self.equipped_weapon: Weapon = hands
        self.equipped_armors: List[Armor] = [nothing, nothing, nothing]
        self.effects: List[Effect] = []
        self.skills: List[Skill] = []

    def get_item_stats(self) -> Stats:
        return self.equipped_weapon.stats + sum((armor.stats for armor in self.equipped_armors), Stats())

    def equip_weapon(self, weapon_name: str):
        weapon = next((w for w in self.weapons if w.name == weapon_name), None)
        if weapon:
            self.unequip_weapon()
            weapon.equipped = True
            self.equipped_weapon = weapon

    def equip_armor(self, armor_name: str):
        armor = next((a for a in self.armors if a.name == armor_name), None)
        if armor:
            self.unequip_armor(armor.piece_type)
            self.equipped_armors[armor.piece_type] = armor
            armor.equipped = True

    def unequip_weapon(self):
        self.equipped_weapon.equipped = False
        self.equipped_weapon = hands

    def unequip_armor(self, piece_type: int):
        self.equipped_armors[piece_type].equipped = False
        self.equipped_armors[piece_type] = nothing
