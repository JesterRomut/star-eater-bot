from datetime import date
from numpy.random import default_rng
from . import config
from ujson import load
# from numba import njit

_answer = load(open(f"{config.static_dir}/storage/answers.json", "r", encoding="UTF-8"))
_r = default_rng()

_luckyNums = [114514, 65535, 1919, 810, 364]


# @njit
# def _shylook(uid: str, ordinal: int) -> tuple[int, int]:
#     seed(sum(map(lambda i: ord(i), uid)) + ordinal)
#     d10, luck = randint(0, 19), randint(0, 100)
#     return d10, luck


# @njit
# def _str_to_int(st: str) -> int:
#     s =
#     return s


def shylook(uid: str) -> int:
    # seed(idnum + date.today().toordinal())
    # d10, luck = randint(0, 19), randint(0, 100)
    # idnum = _str_to_int(uid)
    r = default_rng(sum(map(lambda i: ord(i), uid)) + date.today().toordinal())
    # d10, luck = _shylook(uid, date.today().toordinal())
    d10, luck = r.integers(0, 19), r.integers(0, 100)
    if d10 == 0:
        luck = r.choice(_luckyNums)
    return luck


def answers() -> str:
    chosen = _answer[_r.choice(list(_answer))]["answer"]
    return chosen
