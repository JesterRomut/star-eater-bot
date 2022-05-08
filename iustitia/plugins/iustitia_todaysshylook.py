from nonebot import on_command
from nonebot.matcher import Matcher
from typing import Union
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from ..iustitia import todaysshylook as source

try:
    from _sha512 import sha512 as _sha512
except ImportError:
    from hashlib import sha512 as _sha512

__plugin_name__ = '今日人品'
__plugin_usage__ = "输入 !今日人品 .jrrp 查看人品"

todaysshylook = on_command("todaysshylook", aliases={"jrrp", "今日人品"}, block=True)


@todaysshylook.handle()
async def _(matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
    if isinstance(event, GuildMessageEvent):
        # guild
        idnum = event.get_user_id()
        name = event.sender.card if event.sender.card \
            else event.sender.nickname
        await matcher.finish(source.todaysshylook(int(idnum), name))
    else:
        if isinstance(event, GroupMessageEvent) and (event.anonymous is not None):
            # anonymous
            name = event.anonymous.name
            idnum = name.encode()
            idnum = int.from_bytes(idnum + _sha512(idnum).digest(), 'big')
        else:
            idnum = event.user_id
            name = event.sender.card if event.sender.card \
                else event.sender.nickname
        await matcher.finish(source.todaysshylook(idnum, name))
