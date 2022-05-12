from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot import on_command, get_driver
from nonebot.matcher import Matcher
from typing import Union
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from os import path

__plugin_name__ = '目力娇喘'
__plugin_usage__ = """输入 !嘉登笑 听嘉登笑
输入 !铜叫 听儿童金典
输入 !娇喘 听......"""

config = get_driver().config


class AhegaoCommand:
    def __init__(self, name, aliases: set, filepath: str) -> None:
        self.filepath = filepath
        self.matcher = on_command(name, aliases=aliases, block=True)
        self.matcher.handle()(self.handle)

    async def handle(self, matcher: Matcher, _: Union[PrivateMessageEvent, GroupMessageEvent]):
        file = path.abspath(f"{config.static_dir}/audio/{self.filepath}")
        await matcher.finish(MessageSegment.record(file=f"file:///{file}"))


commands = [
    AhegaoCommand("ahegao", {"娇喘", "恶臭", "目力", '目力娇喘', "喘一个", }, "senpaiRoar.mp3"),
    AhegaoCommand("draedonlaugh", {"嘉登笑", }, "DraedonLaugh.wav"),
    AhegaoCommand("kidscream", {"铜叫", }, "kidscream.mp3")
]
