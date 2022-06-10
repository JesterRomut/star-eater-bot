from ..command import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.params import CommandArg, Depends
from nonebot.adapters import Message
from ..iustitia.occult import shylook, answers
from ..locale import Localisation

todaysshylook = on_command("todaysshylook", aliases={"jrrp", "luck", "shylook", "今日人品"})
answersbook = on_command("answersbook", aliases={"answers", "答案之书", "答案", "翻看答案", })


@todaysshylook.handle()
async def _(matcher: Matcher, event: MessageEvent,
            locale: Localisation = Depends()):
    if isinstance(event, GroupMessageEvent) and (event.anonymous is not None):
        # anonymous
        name = idnum = event.anonymous.name
    else:
        idnum = event.user_id
        name = event.sender.card or event.sender.nickname
    await matcher.finish(locale["todaysshylook"]["default"].format(name=name, luck=shylook(str(idnum))))


@answersbook.handle()
async def _(matcher: Matcher, arg: Message = CommandArg(), locale: Localisation = Depends()):
    if arg := arg.extract_plain_text().strip():
        if len(arg) > 125:
            await matcher.finish(locale["answersbook"]["toolong"])
        await matcher.finish(locale["answersbook"]["default"].format(question=arg, answer=answers()))
    else:
        await matcher.finish(locale["answersbook"]["absent"])

