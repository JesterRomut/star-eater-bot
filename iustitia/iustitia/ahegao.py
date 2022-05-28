from . import config
from os import path


class AhegaoSource:
    __slots__ = ("filepath",)

    def __init__(self, filepath):
        self.filepath = path.abspath(f"{config.static_dir}/audio/{filepath}")
