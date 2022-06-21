from nonebot.log import logger
from nonebot import get_driver
from ..command import on_request
from nonebot.adapters.onebot.v11.event import FriendRequestEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.exception import ActionFailed


config = get_driver().config


# notice & request

friend = on_request(rule=lambda event: isinstance(event, FriendRequestEvent))
group = on_request(rule=lambda event: isinstance(event, GroupRequestEvent))


# CAUTION: MAY CAUSE ACCOUNT BAN
@friend.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    if not config.allow_friend_request:
        return
    try:
        await event.approve(bot)
    except ActionFailed:
        logger.warning("Failed add friend: %s" % event.user_id)
    else:
        logger.info("Added %s to friends" % event.user_id)


@group.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    if event.sub_type != "invite":
        return
    try:
        await event.approve(bot)
    except ActionFailed:
        logger.warning(f"Failed join group: {event.group_id}")
    else:
        logger.info(f"Joined group: {event.group_id}")
