from io import BytesIO
from PIL import Image, ImageColor
from requests import HTTPError

import random
from os import listdir, path

from nonebot import on_command, on_shell_command, get_driver
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace
from nonebot.exception import ParserExit
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from ..iustitia.meme import identify as createidentify
from ..iustitia.meme import rua as generate_rua
from ..iustitia.requests import IustitiaRequest


config = get_driver().config

identify = on_command("identify", aliases={"鉴定", "一眼丁真"}, block=True)

ci_parser = ArgumentParser(usage=".customidentify result [--title title] \
                                   [--color hex:color] [--bordercolor hex:bordercolor] [--image url:url]")
ci_parser.add_argument("result")
ci_parser.add_argument("-T", "--title", required=False)
ci_parser.add_argument("-C", "--color", required=False, default="#ffffff")
ci_parser.add_argument("-B", "--border", required=False, default=None)
ci_parser.add_argument("-I", "--image", required=False, default=None)
customidentify = on_shell_command("identify", parser=ci_parser, aliases={"手动鉴定", "自定义鉴定"}, block=True)

r_parser = ArgumentParser(usage=".rua url:url")
r_parser.add_argument("url")
rua = on_shell_command("rua", parser=r_parser, aliases={"pet", "摸摸", "摸", "摸一下", "摸摸月亮", }, block=True)


@identify.handle()  # .identify
async def _(matcher: Matcher):
    static_dir = config.static_dir
    random.seed(None)
    chosen = listdir(f"{static_dir}/images/identify")
    chosen = chosen[random.randint(0, len(chosen) - 1)]
    chosen = "file:///%s" % (path.abspath(f"{static_dir}/images/identify/{chosen}"))
    # type="flash",
    img = MessageSegment.image(file=chosen)
    await matcher.finish(img)


@rua.handle()
@customidentify.handle()
async def _(matcher: Matcher, _: ParserExit = ShellCommandArgs()):
    await matcher.finish("invalid argument")


@customidentify.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    # stop if too long
    if len(args.result) > 125:
        await session.finish("too long message")

    # init args
    title = None
    headimage = None
    color = None
    border_color = None
    result = f"鉴定为: {args.result}"

    def _hexstrip(c):
        return "#" + c if c[0] != "#" else c

    # request
    if args.image is not None:
        murl = Message(args.image)

        # get url
        for i in murl:
            if i.type == "image":
                url = i.data["url"]
                break
        else:
            url = str(args.image).strip()

        res, err = IustitiaRequest().get(url)
        if err:
            if isinstance(err, HTTPError):
                await matcher.finish(f"invalid image url: {res.status_code}")
            else:
                await matcher.finish("get image failed")

        headimage = Image.open(BytesIO(res.content))
    try:
        color = ImageColor.getcolor(_hexstrip(args.color), "RGB")
        border_color = ImageColor.getcolor(_hexstrip(args.border), "RGB") if args.border is not None else None
    except ValueError:
        await session.finish("invalid color code")
    if args.title is not None:
        title = args.title
        if title[-2::1] != "丁真":
            title += "丁真"

    img = createidentify(title=title, desc=result, color=color, border=border_color, headimage=headimage)
    await matcher.finish(
        # MessageSegment.image(f"base64://{_create_identify(title, result, color, border_color, headimage)}")
        MessageSegment.image(f"base64://{img}")
    )


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