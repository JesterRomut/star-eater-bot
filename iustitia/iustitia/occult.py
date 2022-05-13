from datetime import date
from numpy.random import seed, choice, randint
from . import config
from ujson import load
from numba import njit

_answer = load(open(f"{config.static_dir}/storage/answers.json", "r", encoding="UTF-8"))

_luckyNums = [114514, 65535, 1919, 810, 364]


@njit
def _shylook(fseed: int):
    seed(fseed)
    d10, luck = randint(0, 19), randint(0, 100)
    return d10, luck


def shylook(idnum: int) -> int:
    # seed(idnum + date.today().toordinal())
    # d10, luck = randint(0, 19), randint(0, 100)
    d10, luck = _shylook(idnum + date.today().toordinal())
    if d10 == 0:
        luck = luckyNums[choice(_luckyNums)]
    return luck


def answers() -> str:
    chosen = _answer[choice(list(_answer))]["answer"]
    return chosen
