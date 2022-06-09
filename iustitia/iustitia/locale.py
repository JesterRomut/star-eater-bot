from ujson import load
from . import config


class Languages:
    EN = "en"
    ZH = "zh"


locales = [Languages.EN, Languages.ZH]
locale = {}
for loc in locales:
    locale[loc] = load(open(
        "{}/locale/{}/common.json".format(config.static_dir, loc)
        , encoding="UTF-8"))

