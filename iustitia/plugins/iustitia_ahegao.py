from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot import on_command, get_driver
from nonebot.matcher import Matcher
from typing import Union
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
import os

__plugin_name__ = '目力娇喘'
__plugin_usage__ = """输入 !嘉登笑 听嘉登笑
输入 !铜叫 听儿童金典
输入 !娇喘 听......"""

config = get_driver().config

ahegao = on_command("ahegao", aliases={"娇喘", "恶臭", "目力", '目力娇喘', "喘一个", }, block=True)
draedonlaugh = on_command("draedonlaugh", aliases={"嘉登笑", }, block=True)
kidscream = on_command("kidscream", aliases={"铜叫", }, block=True)


def _get_record(file):
    file = os.path.abspath(f"{config.static_dir}/audio/{file}")
    return MessageSegment.record(file=f"file:///{file}")


@ahegao.handle()
async def _(matcher: Matcher, _: Union[PrivateMessageEvent, GroupMessageEvent]):
    await matcher.finish(_get_record("senpaiRoar.mp3"))


@draedonlaugh.handle()
async def _(matcher: Matcher, _: Union[PrivateMessageEvent, GroupMessageEvent]):
    await matcher.finish(_get_record("DraedonLaugh.wav"))


@kidscream.handle()
async def _(matcher: Matcher, _: Union[PrivateMessageEvent, GroupMessageEvent]):
    await matcher.finish(_get_record("kidscream.mp3"))
