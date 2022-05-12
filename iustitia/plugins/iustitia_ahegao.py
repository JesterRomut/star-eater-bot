from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot import on_command
from nonebot.matcher import Matcher
from typing import Union
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from ..iustitia.ahegao import AhegaoSource


class AhegaoCommand(AhegaoSource):
    def __init__(self, name, aliases: set, filepath: str) -> None:
        super().__init__(filepath)
        self.matcher = on_command(name, aliases=aliases, block=True)
        self.matcher.handle()(self.handle)

    async def handle(self, matcher: Matcher, _: Union[PrivateMessageEvent, GroupMessageEvent]):
        await matcher.finish(MessageSegment.record(file=f"file:///{self.filepath}"))


commands = [
    AhegaoCommand("ahegao", {"娇喘", "恶臭", "目力", '目力娇喘', "喘一个", }, "senpaiRoar.mp3"),
    AhegaoCommand("draedonlaugh", {"嘉登笑", }, "DraedonLaugh.wav"),
    AhegaoCommand("kidscream", {"铜叫", }, "kidscream.mp3"),
    AhegaoCommand("calamitaslaugh", {"灾笑", "终灾笑", "终灾召唤", "四级烧伤"}, "SupremeCalamitasSpawn.wav"),
]
