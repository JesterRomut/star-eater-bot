from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from ..iustitia.ahegao import AhegaoSource


class AhegaoCommand(AhegaoSource):
    __slots__ = ("matcher",)

    def __init__(self, name, aliases: set, filepath: str):
        super().__init__(filepath)
        self.matcher = on_command(name, aliases=aliases, block=True)
        self.matcher.append_handler(self.handle)

    async def handle(self, matcher: Matcher, _: MessageEvent):
        await matcher.finish(MessageSegment.record(file="file:///{}".format(self.filepath)))


commands = (
    AhegaoCommand("ahegao", {"娇喘", "恶臭", "目力", '目力娇喘', "喘一个", }, "senpaiRoar.mp3"),
    AhegaoCommand("draedonlaugh", {"嘉登笑", }, "DraedonLaugh.wav"),
    AhegaoCommand("kidscream", {"铜叫", }, "kidscream.mp3"),
    AhegaoCommand("calamitaslaugh", {"灾笑", "终灾笑", "终灾召唤", "四级烧伤"}, "SupremeCalamitasSpawn.wav"),
)
