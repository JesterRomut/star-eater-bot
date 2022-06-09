from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from ..locale import Localisation
from nonebot.adapters import Message

# with open(f"{config.static_dir}/storage/help.json", "r", encoding="UTF-8") as f:
#     helpmsg = loads(f.read())

helpcommand = on_command("help", aliases={"usage", "帮助", "使用帮助", "说明", "使用说明", "使用方法"}, block=True)


def _get_msg(locale: Localisation):
    # if isinstance(event, GuildMessageEvent):
    #     # guild
    #     r = "\n".join(locale["help"]["guild"])
    # else:
    return "\n".join(locale["help"]["onebot"])


@helpcommand.handle()
async def _(matcher: Matcher, arg: Message = CommandArg(), locale: Localisation = Depends()):
    if arg := arg.extract_plain_text().strip().lower():
        try:
            res = "\n".join(locale["plugin"][arg])
        except KeyError:
            res = _get_msg(locale)
    else:
        res = _get_msg(locale)

    await matcher.finish(res)
