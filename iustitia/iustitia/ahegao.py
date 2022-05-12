from . import config
from os import path


class AhegaoSource:
    def __init__(self, filepath):
        self._filepath = filepath

    @property
    def filepath(self) -> str:
        return path.abspath(f"{config.static_dir}/audio/{self._filepath}")
