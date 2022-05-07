from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.adapters import Message

reverberation = on_command("reverberation", aliases={"复读", "回声", }, block=True)


@reverberation.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if len(arg) > 125:
        await matcher.finish("too long message")
    if arg:
        await matcher.finish(arg)
    else:
        await matcher.finish("invalid message")
