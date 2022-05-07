from nonebot import get_loaded_plugins
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.plugin import Plugin
from nonebot.params import CommandArg
from nonebot.adapters import Message

helpcommand = on_command("help", aliases={"帮助", "使用帮助", "说明", "使用说明", "使用方法"}, block=True)


def _get_pattr(plugin: Plugin, attr: str):
    try:
        return plugin.module.__getattribute__(attr)
    except AttributeError:
        return ""


@helpcommand.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    plugins = list(filter(lambda x: _get_pattr(x, "__plugin_name__"), get_loaded_plugins()))
    arg = arg.extract_plain_text().strip().lower()
    if not arg:
        await matcher.finish(
            '迄今为止包含的要素:\n(输入!help <要素名>查看详细)\n' + '\n'.join(_get_pattr(p, "__plugin_name__") for p in plugins))
    for p in plugins:
        if (p.name.lower() == arg) or (_get_pattr(p, "__plugin_name__") == arg):
            await matcher.finish(_get_pattr(p, "__plugin_usage__"))
