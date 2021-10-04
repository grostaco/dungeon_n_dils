from typing import TypeVar, Iterable, Iterator, overload, Union

T = TypeVar('T')


@overload
def as_gen(x: Iterable[T]) -> Iterator[T]: ...


@overload
def as_gen(x: T) -> Iterator[T]: ...


def as_gen(x: Union[T, Iterable[T]]) -> Iterator[T]:
    if isinstance(x, Iterable) and not isinstance(x, str):
        yield from x
    else:
        yield x



