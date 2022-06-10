from nonebot.log import logger
from nonebot import get_driver
from ..misc import on_request
from nonebot.adapters.onebot.v11.event import FriendRequestEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.exception import ActionFailed


config = get_driver().config


# notice & request


# async def _friend(event: Event):
#     return isinstance(event, FriendRequestEvent)


# async def _group(event: Event):
#     return isinstance(event, GroupRequestEvent)


friend = on_request(rule=lambda event: isinstance(event, FriendRequestEvent))
group = on_request(rule=lambda event: isinstance(event, GroupRequestEvent))


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
            logger.warning("Failed join group: %s" % event.group_id)
            raise
        else:
            logger.info("Joined group: %s" % event.group_id)






