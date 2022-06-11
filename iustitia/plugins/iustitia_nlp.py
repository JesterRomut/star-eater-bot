from nonebot.params import EventToMe, EventPlainText
from nonebot.matcher import Matcher
from numpy.random import default_rng
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent, MessageEvent
from nonebot.typing import T_State
from ..iustitia.pinyin import pinyin, Match
from ..command import on_command, on_notice, on_message
from .iustitia_occult import todaysshylook

_r = default_rng()

nlp = on_message(priority=100)
nlp_c = on_command("", priority=99)
poke = on_notice(rule=lambda event: isinstance(event, PokeNotifyEvent))
# todaysshylook = require("iustitia_occult").todaysshylook


def getquestion() -> str:
    return "¿" if _r.integers(0, 9) == 0 else "?"


@nlp.handle()
async def _(matcher: Matcher, to_me: bool = EventToMe(), arg: str = EventPlainText()):
    to_me = to_me or Match.startswith("ftsb", pinyin(arg))
    if to_me:
        await matcher.finish(getquestion())


@nlp_c.handle()
async def _(bot: Bot, state: T_State, event: MessageEvent, arg: str = EventPlainText()):
    if Match.startswith("jrrp", pinyin(arg[1:])):
        await todaysshylook().run(bot=bot, event=event, state=state)


@poke.handle()
async def _(matcher: Matcher, event: PokeNotifyEvent):
    if event.target_id == event.self_id:
        await matcher.finish(getquestion(), at_sender=True)
