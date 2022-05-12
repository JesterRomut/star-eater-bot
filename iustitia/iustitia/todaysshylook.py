from datetime import date
import random

luckyNums = [114514, 65535, 1919, 810]


def todaysshylook(idnum: int, name: str) -> str:
    random.seed(idnum + date.today().toordinal())
    d10, shylook = random.randint(0, 19), random.randint(0, 100)
    if d10 == 0:
        shylook = luckyNums[random.randint(0, len(luckyNums) - 1)]
    return "%s 今天的人品指数: %d" % (name, shylook)
