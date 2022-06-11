from fake_useragent import UserAgent
from typing import Optional
from httpx import AsyncClient, HTTPError, Response

_ua = UserAgent(fallback='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0')


def get_ua() -> dict:
    return {
        "Accept": "image/*",
        "User-Agent": _ua.random,
    }


async def imageget(url: str) -> tuple[Response, Optional[HTTPError]]:
    res, err = None, None
    try:
        async with AsyncClient(headers=get_ua()) as client:
            res = await client.get(url)
        res.raise_for_status()
    except HTTPError as e:
        err = e
    else:
        err = None
    # if int(res.headers['Content-length']) > 1048576:  # 1 MB
    #     await matcher.finish("image too big")
    return res, err
