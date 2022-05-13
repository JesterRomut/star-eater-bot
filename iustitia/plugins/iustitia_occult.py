from nonebot import on_command
from nonebot.matcher import Matcher
from typing import Union
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.params import CommandArg, Depends
from nonebot.adapters import Message
from ..iustitia.occult import shylook, answers
from ..locale import Localisation
from numba import njit

todaysshylook = on_command("todaysshylook", aliases={"jrrp", "luck", "shylook", "今日人品"}, block=True)
answersbook = on_command("answersbook", aliases={"answers", "答案之书", "答案", "翻看答案", }, block=True)


@njit
def _str_to_int(st: str) -> int:
    s = 0
    for i in st:
        s += ord(i)
    return s


@todaysshylook.handle()
async def _(matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent],
            locale: Localisation = Depends()):
    # locale = localisation(event, "todaysshylook"
    if isinstance(event, GuildMessageEvent):
        # guild
        idnum = event.user_id
        name = event.sender.nickname
    else:
        if isinstance(event, GroupMessageEvent) and (event.anonymous is not None):
            # anonymous
            name = event.anonymous.name
            idnum = _str_to_int(name)
        else:
            idnum = event.user_id
            name = event.sender.card if event.sender.card \
                else event.sender.nickname
    await matcher.finish(locale["todaysshylook"]["default"].format(name=name, luck=shylook(idnum)))


@answersbook.handle()
async def _(matcher: Matcher, arg: Message = CommandArg(), locale: Localisation = Depends()):
    arg = arg.extract_plain_text().strip()
    # locale = localisation(event, "answersbook")
    if not arg:
        await matcher.finish(locale["answersbook"]["absent"])
    if len(arg) > 125:
        await matcher.finish(locale["answersbook"]["toolong"])
    await matcher.finish(locale["answersbook"]["default"].format(question=arg, answer=answers()))
