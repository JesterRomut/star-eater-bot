from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from .iustitia.locale import locale
from typing import Union
from ujson import load
from pydantic import BaseModel


class Setting(BaseModel):
    lang: Union[str, bool] = False
    banned: bool = False


class Localisation(dict):
    def __init__(self, matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
        memory = load(open("memory.json", "r"))["settings"]
        arg = {"locale": "zh"}

        def _check_data(data: dict):
            data = Setting(**data)
            if data.banned:
                raise FinishedException("banned")
            if data.lang:
                arg["locale"] = data.lang

        _check_data(memory["global"])
        if isinstance(event, GuildMessageEvent):
            _check_data(memory["guild"]["global"])
            guild_id = str(event.guild_id)
            channel_id = str(event.channel_id)
            guild = memory["guild"]["guild"].get(guild_id, {"global": {}, "channel": {}})
            _check_data(guild["global"])
            _check_data(guild["channel"].get(channel_id, {}))
        elif isinstance(event, GroupMessageEvent):
            _check_data(memory["onebot"]["global"])
            group_id = str(event.group_id)
            _check_data(memory["onebot"]["group"].get(group_id, {"global": {}})["global"])
        user_id = str(event.user_id)
        _check_data(memory["onebot"]["user"].get(user_id, {}))

        super().__init__(locale[arg["locale"]]["plugin"][matcher.plugin_name])
