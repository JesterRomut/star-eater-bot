from . import config
from os import path


class AhegaoSource:
    __slots__ = ("filepath",)

    def __init__(self, filepath):
        self.filepath: str = path.abspath("{}/audio/{}".format(config.static_dir, filepath))
