from typing import TypedDict, Unpack, Any, Type, Mapping, TypeVar, cast

def foo(a: str | None = None):
    print(a)

def bar(b: int | None = None):
    if b is None:
        b = 0
    print(b + 1)

class FooProps(TypedDict, total=False):
    a: str | None

class BarProps(TypedDict, total=False):
    b: int | None

class FooBarProps(FooProps, BarProps):
    pass

T = TypeVar("T")

def into(kind: Type[T], kwargs: Mapping[str, Any]) -> T:
    """
    Filters a dictionary to match the keys defined in a TypedDict class.

    NOTE: This does not perform strict type-checking of the dict values.
    """
    return cast(T, {k: v for k, v in kwargs.items() if k in kind.__annotations__})

def foobar(times: int, **kwargs: Unpack[FooBarProps]):
    for _ in range(times):
        foo(**into(FooProps, kwargs))  # MyPy-safe
        bar(**into(BarProps, kwargs))  # MyPy-safe

# Unexpected keyword argument "baz" for "foobar"
foobar(5, baz=10)  # type: ignore

foobar(1, a="hi", b=5)
