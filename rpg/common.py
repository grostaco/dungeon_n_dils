from __future__ import annotations


class Stats:
    def __init__(self, hp: float = .0,
                 defense: float = .0,
                 atk: float = .0,
                 intelligence: float = .0,
                 ):
        self.hp = hp
        self.defense = defense
        self.atk = atk
        self.int = intelligence

    def __add__(self, other: Stats):
        return Stats(self.hp + other.hp, self.defense + other.defense,
                     self.atk + other.atk, self.int + other.int)

    def __sub__(self, other):
        return self + -1 * other

    def __mul__(self, multiplier: float):
        return Stats(self.hp * multiplier, self.defense * multiplier,
                     self.atk * multiplier, self.int * multiplier)

