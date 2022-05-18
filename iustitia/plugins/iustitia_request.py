from nonebot.log import logger
from nonebot import on_request, on_notice, on_message, get_driver
from nonebot.adapters.onebot.v11.event import FriendRequestEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.rule import to_me
from numpy.random import default_rng


config = get_driver().config
_r = default_rng()


# notice & request
def getquestion():
    res = "?"
    if _r.integers(0, 9) == 0:
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


# CAUTION: MAY CAUSE ACCOUNT BAN
@friend.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    if config.allow_friend_request:
        try:
            await event.approve(bot)
        except ActionFailed:
            pass
        else:
            logger.info("Added %s to friends" % event.user_id)


@group.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    if event.sub_type == "invite":
        try:
            await event.approve(bot)
        except ActionFailed:
            raise
        else:
            logger.info("Joined group: %s" % event.group_id)


@poke.handle()
async def _(matcher: Matcher, event: PokeNotifyEvent):
    if event.target_id == event.self_id:
        if event.group_id is not None:
            # group
            # MessageSegment.at(event.user_id) +
            await matcher.finish(MessageSegment.text(getquestion()), at_sender=True)
        await matcher.finish(getquestion())


@nlp.handle()
async def _(matcher: Matcher):
    await matcher.finish(getquestion())
