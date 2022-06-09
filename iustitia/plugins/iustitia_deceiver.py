from numpy.random import default_rng
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, MessageEvent
from nonebot.adapters.onebot.exception import ActionFailed
from nonebot.params import Depends
from ..locale import Localisation

_r = default_rng()

rwkk = on_command("rwkk", aliases={'嘉登色图', "色图", }, block=True)


@rwkk.handle()
async def _(matcher: Matcher, event: MessageEvent, bot: Bot,
            locale: Localisation = Depends()):
    chosen = _r.choice(locale["namelist"])
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
    try:
        await bot.send_private_msg(user_id=event.user_id, message=Message([res]))
    except ActionFailed:
        await matcher.finish(locale["mustfriend"])
    else:
        await matcher.finish(MessageSegment.text(locale["success"]), at_sender=True)
