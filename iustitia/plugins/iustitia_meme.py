from io import BytesIO
from PIL import Image, ImageColor
from nonebot import get_driver
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from ..iustitia.meme import custom_identify, random_identify, rua_gif
from ..iustitia.requests import imageget
from ..command import defaultparserexit, on_command, on_shell_command
from httpx import HTTPStatusError
from asyncio import create_task
from ..locale import Localisation, Locale


config = get_driver().config

identify = on_command("identify", aliases={"鉴定", "一眼丁真"})

_c_parser = ArgumentParser(usage=".customidentify result [--title title] \
                                   [--color hex:color] [--bordercolor hex:bordercolor] [--image url:url]")
_c_parser.add_argument("result")
_c_parser.add_argument("-T", "--title", required=False)
_c_parser.add_argument("-C", "--color", required=False, default="#ffffff")
_c_parser.add_argument("-B", "--border", required=False, default=None)
_c_parser.add_argument("-I", "--image", required=False, default=None)
customidentify = on_shell_command("customidentify", parser=_c_parser, aliases={"手动鉴定", "自定义鉴定"})
customidentify.append_handler(defaultparserexit)

_r_parser = ArgumentParser(usage=".rua url:url")
_r_parser.add_argument("url")
rua = on_shell_command("rua", parser=_r_parser, aliases={"pet", "摸摸", "摸", "摸一下", "摸摸月亮", })
rua.append_handler(defaultparserexit)


@identify.handle()  # .identify
async def _(matcher: Matcher):
    await matcher.finish(
        MessageSegment.image(file="file:///{}".format(await random_identify()))
    )


async def _getimage(url: str, matcher: Matcher, locale: Localisation):
    for ms in Message(url):
        if ms.type == "image":
            url = ms.data["url"]
            break
    else:
        url = str(url).strip()

    res, err = await imageget(url)
    if isinstance(err, HTTPStatusError):
        await matcher.finish(locale["meme"]["invalid"].format(code=res.status_code))
    elif err:
        await matcher.finish(locale["meme"]["failed"])
    return res


def _hexstrip(c):
    return "#" + c if c[0] != "#" else c


async def _none(): return


@customidentify.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs(), locale: Localisation = Locale()):
    # stop if too long
    if len(args.result) > 125:
        await session.finish("too long message")

    # init args
    title = None
    # headimage = None
    color = None
    border_color = None
    result = "鉴定为: {}".format(args.result)

    getimage = create_task(
        _getimage(args.image, matcher, locale) if args.image else _none()
    )

    try:
        color = ImageColor.getcolor(_hexstrip(args.color), "RGB")
        border_color = ImageColor.getcolor(_hexstrip(args.border), "RGB") if args.border is not None else None
    except ValueError:
        await matcher.finish(locale["meme"]["invalidcolor"])

    if args.title:
        title = args.title
        if title[-2::1] != "丁真":
            title += "丁真"

    # request
    res = await getimage
    headimage = Image.open(BytesIO(res.content)) if res else None

    img = await custom_identify(title=title, desc=result, color=color, border=border_color, headimage=headimage)
    await matcher.finish(
        # MessageSegment.image(f"base64://{_create_identify(title, result, color, border_color, headimage)}")
        MessageSegment.image("base64://{}".format(img))
    )


@rua.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs(), locale: Localisation = Locale()):
    res = await _getimage(args.url, matcher, locale)

    with Image.open(BytesIO(res.content)) as rimg:
        rimg = rimg.convert("RGBA")
        g = rua_gif(rimg)
    await matcher.finish(MessageSegment.image("base64://{}".format(g)), at_sender=True)
