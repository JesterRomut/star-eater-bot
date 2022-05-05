from nonebot import on_command
from nonebot.matcher import Matcher
from typing import Union
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from datetime import date
import random

try:
    from _sha512 import sha512 as _sha512
except ImportError:
    from hashlib import sha512 as _sha512

__plugin_name__ = '今日人品'
__plugin_usage__ = "输入 !今日人品 .jrrp 查看人品"

todaysshylook = on_command("todaysshylook", aliases={"jrrp", "今日人品"}, block=True)

luckyNums = [114514, 65535, 1919, 810]


@todaysshylook.handle()
async def _(matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent]):
    if isinstance(event, GroupMessageEvent) and (event.anonymous is not None):
        # anonymous
        name = event.anonymous.name
        idnum = name.encode()
        idnum = int.from_bytes(idnum + _sha512(idnum).digest(), 'big')
    else:
        idnum = event.user_id
        name = event.sender.card if event.sender.card \
            else event.sender.nickname
    random.seed(idnum + date.today().toordinal())
    d10, shylook = random.randint(0, 19), random.randint(0, 100)
    if d10 == 0:
        shylook = luckyNums[random.randint(0, len(luckyNums) - 1)]
    await matcher.finish("%s 今天的人品指数: %d" % (name, shylook))
