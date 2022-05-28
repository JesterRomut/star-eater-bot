from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException
from .iustitia.locale import locale
from typing import Union, Callable, Any
from ujson import load
from pydantic import BaseModel


class Setting(BaseModel):
    lang: Union[str, bool] = False


def _check_data(
        func: Callable[[Setting], Any],
        event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]
) -> None:
    memory = load(open("memory.json", "r"))["settings"]

    def _check(rawdata: dict):
        try:
            func(Setting(**rawdata))
        except FinishedException as e:
            raise e

    _check(memory["global"])
    if isinstance(event, GuildMessageEvent):
        _check(memory["guild"]["global"])
        guild_id = str(event.guild_id)
        channel_id = str(event.channel_id)
        guild = memory["guild"]["guild"].get(guild_id, {"global": {}, "channel": {}})
        _check(guild["global"])
        _check(guild["channel"].get(channel_id, {}))
    elif isinstance(event, GroupMessageEvent):
        _check(memory["onebot"]["global"])
        group_id = str(event.group_id)
        _check(memory["onebot"]["group"].get(group_id, {"global": {}})["global"])
    user_id = str(event.user_id)
    _check(memory["onebot"]["user"].get(user_id, {}))


class Localisation(dict):
    __slots__ = ()

    def __init__(self, matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
        arg = {"locale": "zh"}

        def _check(data: Setting):
            if data.lang:
                arg["locale"] = data.lang

        _check_data(_check, event)

        super().__init__(locale[arg["locale"]]["plugin"][matcher.plugin_name])
