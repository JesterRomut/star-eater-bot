from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.exception import FinishedException
from .iustitia.locale import locale as _locale
from typing import Union, Callable, Any
from ujson import load
from pydantic import BaseModel
from collections import Mapping


class Setting(BaseModel):
    lang: Union[str, bool] = False


def _check_data(
        func: Callable[[Setting], Any],
        event: Event
) -> None:
    memory = load(open("memory.json", "r"))["settings"]

    def _check(rawdata: dict):
        try:
            func(Setting(**rawdata))
        except FinishedException as e:
            raise e

    _check(memory["global"])
    # if isinstance(event, GuildMessageEvent):
    #     _check(memory["guild"]["global"])
    #     guild_id = str(event.guild_id)
    #     channel_id = str(event.channel_id)
    #     guild = memory["guild"]["guild"].get(guild_id, {"global": {}, "channel": {}})
    #     _check(guild["global"])
    #     _check(guild["channel"].get(channel_id, {}))
    # elif isinstance(event, GroupMessageEvent):
    _check(memory["onebot"]["global"])
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        _check(memory["onebot"]["group"].get(group_id, {"global": {}})["global"])
    user_id = str(event.user_id)
    _check(memory["onebot"]["user"].get(user_id, {}))


class Localisation(Mapping):
    __slots__ = ("_dict", "_hash")

    def __init__(self, event: Event):
        arg = {"locale": "zh"}

        # def _check(data: Setting):
        #     if data.lang:
        #         arg["locale"] = data.lang
        #
        # _check_data(_check, event)

        self._dict = dict(_locale[arg["locale"]])
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._dict)

    def __hash__(self):
        if self._hash is None:
            h = 0
            for key, value in iteritems(self._dict):
                h ^= hash((key, value))
            self._hash = h
        return self._hash


async def _get_locale(event: Event) -> Localisation:
    return Localisation(event)


def Locale() -> Localisation:
    return Depends(_get_locale)
