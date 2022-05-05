from nonebot.log import logger
from nonebot import on_request, on_notice, on_message
from nonebot.adapters.onebot.v11.event import FriendRequestEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.rule import to_me
import random


def getquestion():
    res = "?"
    random.seed(None)
    if random.randint(0, 9) == 0:
        res = "¿"
    return res


async def _friend(event: Event):
    return isinstance(event, FriendRequestEvent)


async def _group(event: Event):
    return isinstance(event, GroupRequestEvent)


async def _poke(event: Event):
    return isinstance(event, PokeNotifyEvent)

friend = on_request(rule=_friend)
group = on_request(rule=_group)

poke = on_notice(rule=_poke)

nlp = on_message(rule=to_me(), block=True, priority=100)


@friend.handle()
async def friendhandle(bot: Bot, event: FriendRequestEvent):
    logger.info("Added %s to friends" % event.user_id)
    try:
        await event.approve(bot)
    except ActionFailed:
        pass


@group.handle()
async def grouphandle(bot: Bot, event: GroupRequestEvent):
    if event.sub_type == "invite":
        logger.info("Joined group: %s" % event.group_id)
        try:
            await event.approve(bot)
        except ActionFailed:
            pass


@poke.handle()
async def _(matcher: Matcher, event: PokeNotifyEvent):
    if event.target_id == event.self_id:
        print(event.group_id)
        if event.group_id is not None:
            # group
            await matcher.finish(MessageSegment.at(event.user_id) + MessageSegment.text(getquestion()))
        await matcher.finish(getquestion())


@nlp.handle()
async def nlp(matcher: Matcher):
    await matcher.finish(getquestion())
