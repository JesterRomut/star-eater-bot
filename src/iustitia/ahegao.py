from . import config
from base64 import b64encode


class AhegaoSource:
    __slots__ = ("file64",)

    def __init__(self, filepath):
        with open(f"{config.static_dir}/audio/{filepath}", "rb") as file:
            res = file.read()
        self.file64: str = b64encode(res).decode()
