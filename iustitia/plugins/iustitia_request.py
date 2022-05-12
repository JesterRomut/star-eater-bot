from nonebot.log import logger
from nonebot import on_request, on_notice, on_message, get_driver
from nonebot.adapters.onebot.v11.event import FriendRequestEvent, GroupRequestEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent, PrivateMessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor
from nonebot.rule import to_me
from nonebot.exception import IgnoredException
from typing import Union
from ujson import loads
import random

config = get_driver().config

# preprocessor


@event_preprocessor
async def _(event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
    user_id = str(event.user_id)

    if user_id in config.superusers:
        return

    with open("memory.json", "r") as memory:
        rawperm = loads(memory.read())["perm"]

    def _raise_perm(p):
        try:
            user = p[user_id]
        except KeyError:
            pass
        else:
            if user.get("banned", False) is True:
                raise IgnoredException("ignored user:%s" % user_id)

    if isinstance(event, GuildMessageEvent):
        # guild
        perm = rawperm["guild"]["user"]
        _raise_perm(perm)
    else:
        perm = rawperm["onebot"]["user"]
        _raise_perm(perm)


# notice & request

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


# CAUTION: MAY CAUSE ACCOUNT BAN
@friend.handle()
async def _(bot: Bot, event: FriendRequestEvent):
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
            await matcher.finish(MessageSegment.at(event.user_id) + MessageSegment.text(getquestion()))
        await matcher.finish(getquestion())


@nlp.handle()
async def _(matcher: Matcher):
    await matcher.finish(getquestion())
