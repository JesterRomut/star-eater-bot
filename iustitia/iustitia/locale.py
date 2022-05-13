from ujson import load
from . import config


class Languages:
    EN = "en"
    ZH = "zh"


locales = [Languages.EN, Languages.ZH]
locale = {}
for loc in locales:
    locale[loc] = load(open(f"{config.static_dir}/locale/{loc}/common.json", encoding="UTF-8"))

