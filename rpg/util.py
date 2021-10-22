from typing import TypeVar, Iterable, Iterator, overload, Union, Callable, TYPE_CHECKING
from .common import Stats
from .characters import Character

T = TypeVar('T')
mod_func = Callable[[float], float]
identity = lambda x: x


@overload
def as_gen(x: Iterable[T]) -> Iterator[T]: ...


@overload
def as_gen(x: T) -> Iterator[T]: ...


def as_gen(x: Union[T, Iterable[T]]) -> Iterator[T]:
    if isinstance(x, Iterable) and not isinstance(x, str):
        yield from x
    else:
        yield x


def stat_mod(
        hp: mod_func = identity,
        defense: mod_func = identity,
        atk: mod_func = identity,
        intelligence: mod_func = identity,
) -> Callable[[Character], Stats]:
    def _wrap(character: Character):
        return Stats(
            hp(character.stats.hp),
            defense(character.stats.defense),
            atk(character.stats.atk),
            intelligence(character.stats.int),
        )

    return _wrap
