"""Pure Python dice rolling engine."""

import random
from typing import List


def d4() -> int:
    return random.randint(1, 4)


def d6() -> int:
    return random.randint(1, 6)


def d8() -> int:
    return random.randint(1, 8)


def d10() -> int:
    return random.randint(1, 10)


def d12() -> int:
    return random.randint(1, 12)


def d20() -> int:
    return random.randint(1, 20)


def d100() -> int:
    return random.randint(1, 100)


def roll(sides: int, count: int = 1, modifier: int = 0) -> dict:
    """Roll dice and return structured result."""
    dice: List[int] = [random.randint(1, sides) for _ in range(count)]
    total = sum(dice) + modifier
    return {"dice": dice, "modifier": modifier, "total": total}
