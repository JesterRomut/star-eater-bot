from io import BytesIO
from PIL import Image, ImageColor
from nonebot import on_command, on_shell_command, get_driver
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs, Depends
from nonebot.rule import ArgumentParser, Namespace
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from ..iustitia.meme import custom_identify, random_identify, rua_gif
from ..iustitia.requests import imageget
from ..misc import defaultparserexit
from httpx import HTTPStatusError
from ..locale import Localisation


config = get_driver().config

identify = on_command("identify", aliases={"鉴定", "一眼丁真"}, block=True)

_c_parser = ArgumentParser(usage=".customidentify result [--title title] \
                                   [--color hex:color] [--bordercolor hex:bordercolor] [--image url:url]")
_c_parser.add_argument("result")
_c_parser.add_argument("-T", "--title", required=False)
_c_parser.add_argument("-C", "--color", required=False, default="#ffffff")
_c_parser.add_argument("-B", "--border", required=False, default=None)
_c_parser.add_argument("-I", "--image", required=False, default=None)
customidentify = on_shell_command("customidentify", parser=_c_parser, aliases={"手动鉴定", "自定义鉴定"}, block=True)
customidentify.append_handler(defaultparserexit)

_r_parser = ArgumentParser(usage=".rua url:url")
_r_parser.add_argument("url")
rua = on_shell_command("rua", parser=_r_parser, aliases={"pet", "摸摸", "摸", "摸一下", "摸摸月亮", }, block=True)
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
        await matcher.finish(locale["invalid"].format(code=res.status_code))
    elif err:
        await matcher.finish(locale["failed"])
    return res


def _hexstrip(c):
    return "#" + c if c[0] != "#" else c


@customidentify.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs(), locale: Localisation = Depends()):
    # stop if too long
    if len(args.result) > 125:
        await session.finish("too long message")

    # init args
    title = None
    headimage = None
    color = None
    border_color = None
    result = "鉴定为: {}".format(args.result)

    try:
        color = ImageColor.getcolor(_hexstrip(args.color), "RGB")
        border_color = ImageColor.getcolor(_hexstrip(args.border), "RGB") if args.border is not None else None
    except ValueError:
        await session.finish(locale["invalidcolor"])

    if args.title is not None:
        title = args.title
        if title[-2::1] != "丁真":
            title += "丁真"

    # request
    if args.image is not None:
        # get url
        res = await _getimage(args.image, matcher, locale)
        headimage = Image.open(BytesIO(res.content))

    img = await custom_identify(title=title, desc=result, color=color, border=border_color, headimage=headimage)
    await matcher.finish(
        # MessageSegment.image(f"base64://{_create_identify(title, result, color, border_color, headimage)}")
        MessageSegment.image("base64://{}".format(img))
    )


@rua.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs(), locale: Localisation = Depends()):
    res = await _getimage(args.url, matcher, locale)

    with Image.open(BytesIO(res.content)) as rimg:
        rimage = rimg.convert("RGBA")

        g = await rua_gif(rimage)

    await matcher.finish(MessageSegment.image("base64://{}".format(g)), at_sender=True)
