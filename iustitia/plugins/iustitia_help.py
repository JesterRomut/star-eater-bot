from nonebot import get_driver
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from typing import Union
from ujson import loads

config = get_driver().config

with open(f"{config.static_dir}/storage/help.json", "r", encoding="UTF-8") as f:
    helpmsg = loads(f.read())

helpcommand = on_command("help", aliases={"帮助", "使用帮助", "说明", "使用说明", "使用方法"}, block=True)


# def _get_pattr(plugin: Plugin, attr: str):
#     try:
#         return plugin.module.__getattribute__(attr)
#     except AttributeError:
#         return ""


@helpcommand.handle()
async def _(matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent],
            arg: Message = CommandArg()):
    # plugins = list(filter(lambda x: _get_pattr(x, "__plugin_name__"), get_loaded_plugins()))
    # arg = arg.extract_plain_text().strip().lower()
    # if not arg:
    #     await matcher.finish(
    #         '迄今为止包含的要素:\n(输入!help <要素名>查看详细)\n' + '\n'.join(_get_pattr(p, "__plugin_name__") for p in plugins))
    # for p in plugins:
    #     if (p.name.lower() == arg) or (_get_pattr(p, "__plugin_name__") == arg):
    #         await matcher.finish(_get_pattr(p, "__plugin_usage__"))
    arg = arg.extract_plain_text().strip().lower()

    def _get_msg():
        if isinstance(event, GuildMessageEvent):
            # guild
            r = "\n".join(helpmsg["help"]["guild"])
        else:
            r = "\n".join(helpmsg["help"]["onebot"])
        return r

    if not arg:
        res = _get_msg()
    else:
        try:
            res = "\n".join(helpmsg["plugin"][arg])
        except KeyError:
            res = _get_msg()

    await matcher.finish(res)
