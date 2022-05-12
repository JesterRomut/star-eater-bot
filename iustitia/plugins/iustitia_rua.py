from PIL import Image
from nonebot import on_shell_command, get_driver
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.exception import ParserExit
from nonebot.rule import ArgumentParser, Namespace
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from io import BytesIO
from ..iustitia.requests import IustitiaRequest
from ..iustitia.meme import rua as generate_rua
from requests import HTTPError

__plugin_name__ = '摸摸月亮'
__plugin_usage__ = """输入 !摸摸 图片url 摸摸图片"""

config = get_driver().config

r_parser = ArgumentParser(usage=".rua url:url")
r_parser.add_argument("url")
rua = on_shell_command("rua", parser=r_parser, aliases={"pet", "摸摸", "摸", "摸一下", "摸摸月亮", }, block=True)


@rua.handle()
async def _(matcher: Matcher, _: ParserExit = ShellCommandArgs()):
    await matcher.finish("invalid argument")


@rua.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    murl = Message(args.url)

    # get url
    for ms in murl:
        if ms.type == "image":
            url = ms.data["url"]
            break
    else:
        url = str(args.url).strip()

    res, err = IustitiaRequest().get(url)
    if err:
        if isinstance(err, HTTPError):
            await matcher.finish(f"invalid image url: {res.status_code}")
        else:
            await matcher.finish("get image failed")

    rimage = Image.open(BytesIO(res.content))
    rimage = rimage.convert("RGBA")

    g = generate_rua(rimage)
    await matcher.finish(MessageSegment.image(f"base64://{g}"))
