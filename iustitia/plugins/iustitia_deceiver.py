import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Message
from nonebot.matcher import Matcher
from typing import Union
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11.exception import ApiNotAvailable, ActionFailed

__plugin_name__ = '嘉登色图'
__plugin_usage__ = """输入 !rwkk 看好康的
绝对绝对不是rickroll"""

nameList = [
    "futa加灯打疯凶药",
    "DoubleD_ckDude爆炒橙子菠萝",
    "橙子在左菠萝在右妞子在中",
    "四手霸王电锯反攻妞子",
    "黑丝XM05捆绑丸吞",
    "监禁？俘获？嘉登的命运究竟是什么",
]

rwkk = on_command("rwkk", aliases={'嘉登色图', "色图", }, block=True)


@rwkk.handle()
async def _(matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent], bot: Bot):
    random.seed(None)
    chosen = nameList[random.randint(0, len(nameList) - 1)]
    res = MessageSegment.share(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        title=chosen + " [4K 60FPS]",
        content=chosen,
        # image_url = "file:///%s"%(os.path.abspath("static/images/draedonstrip.png")),
        image="https://calamitymod.wiki.gg/images/thumb/3/34/Exo_Mechs.png/450px-Exo_Mechs.png"
    )
    if isinstance(event, PrivateMessageEvent):
        # private chat
        await matcher.finish(res)
    # group
    user_id = event.user_id
    try:
        await bot.send_private_msg(user_id=user_id, message=Message([res]))
    except (ApiNotAvailable, ActionFailed):
        await matcher.finish("这个要加好友私发")
    else:
        await matcher.finish(MessageSegment.at(user_id) + MessageSegment.text("已私发"))
