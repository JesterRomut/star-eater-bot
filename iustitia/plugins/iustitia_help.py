from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from ..locale import Localisation
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from typing import Union

# with open(f"{config.static_dir}/storage/help.json", "r", encoding="UTF-8") as f:
#     helpmsg = loads(f.read())

helpcommand = on_command("help", aliases={"usage", "帮助", "使用帮助", "说明", "使用说明", "使用方法"}, block=True)


@helpcommand.handle()
async def _(matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent],
            arg: Message = CommandArg(), locale: Localisation = Depends()):
    arg = arg.extract_plain_text().strip().lower()

    def _get_msg():
        if isinstance(event, GuildMessageEvent):
            # guild
            r = "\n".join(locale["help"]["guild"])
        else:
            r = "\n".join(locale["help"]["onebot"])
        return r

    if not arg:
        res = _get_msg()
    else:
        try:
            res = "\n".join(locale["plugin"][arg])
        except KeyError:
            res = _get_msg()

    await matcher.finish(res)
