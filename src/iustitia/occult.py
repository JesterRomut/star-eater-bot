from datetime import date
from numpy.random import default_rng
from . import config
from ujson import load

_answer = load(open(f"{config.static_dir}/storage/answers.json", "r", encoding="UTF-8"))
_r = default_rng()

_luckyNums = (114514, 65535, 1919, 810, 364)


def shylook(uid: str) -> int:
    r = default_rng(sum(map(lambda i: ord(i), uid)) + date.today().toordinal())
    d10, luck = r.integers(0, 19), r.integers(0, 100)
    return r.choice(_luckyNums) if d10 == 0 else luck


def answers() -> str:
    return _answer[_r.choice(list(_answer))]["answer"]
