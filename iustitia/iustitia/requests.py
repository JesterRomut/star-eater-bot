from fake_useragent import UserAgent
from typing import Union
import requests

_ua = UserAgent(fallback='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0')


class IustitiaRequest:
    @property
    def header(self) -> dict:
        dic = {
            "Accept": "image/*",
            "User-Agent": _ua.random,
        }
        return dic

    def get(self, url: str) -> tuple[requests.Response, Union[bool, requests.RequestException]]:
        res = None
        try:
            res = requests.get(url, headers=self.header)
            res.raise_for_status()
        except (requests.HTTPError, requests.RequestException) as e:
            err = e
        else:
            err = False
        # if int(res.headers['Content-length']) > 1048576:  # 1 MB
        #     await matcher.finish("image too big")
        return res, err