from nonebot.params import EventToMe, EventPlainText
from nonebot.matcher import Matcher
from nonebot import on_notice, on_message, on_command, require, get_plugin
from numpy.random import default_rng
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent, MessageEvent
from nonebot.typing import T_State
from pypinyin import pinyin as _pinyin
from functools import partial
from pypinyin import STYLE_FIRST_LETTER
from pypinyin_dict.phrase_pinyin_data import cc_cedict

# from iustitia_occult import todaysshylook

cc_cedict.load()

_r = default_rng()

pinyin = partial(_pinyin, style=STYLE_FIRST_LETTER, heteronym=True, strict=True, errors="ignore")

nlp = on_message(block=True, priority=100)
nlp_c = on_command("", block=True, priority=99)
poke = on_notice(rule=lambda event: isinstance(event, PokeNotifyEvent))
todaysshylook = require("iustitia_occult").todaysshylook


def getquestion() -> str:
    return "¿" if _r.integers(0, 9) == 0 else "?"


def matchpinyin(st: str, pn: list[list[str]]) -> bool:
    if not pn:
        return False
    res = True
    for i, letter in enumerate(pn):
        try:
            if st[i] not in letter:
                res = False
        except IndexError:
            break
    return res


@nlp.handle()
async def _(matcher: Matcher, to_me: bool = EventToMe(), arg: str = EventPlainText()):
    to_me = to_me or matchpinyin("ftsb", pinyin(arg))
    if to_me:
        await matcher.finish(getquestion())


@nlp_c.handle()
async def _(bot: Bot, state: T_State, event: MessageEvent, arg: str = EventPlainText()):
    arg = arg[1:]
    if matchpinyin("jrrp", pinyin(arg)):
        await todaysshylook().run(bot=bot, event=event, state=state)


@poke.handle()
async def _(matcher: Matcher, event: PokeNotifyEvent):
    if event.target_id == event.self_id:
        await matcher.finish(getquestion(), at_sender=True)
