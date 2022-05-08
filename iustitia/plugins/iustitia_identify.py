from io import BytesIO
from base64 import b64encode
from PIL import Image, ImageDraw, ImageFont, ImageColor
from fake_useragent import UserAgent
import requests

import random
import os

from nonebot import on_command, on_shell_command, get_driver
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace
from nonebot.exception import ParserExit
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from ..imagelib import imgresize
from ..iustitia.identify import identify as createidentify

__plugin_name__ = '一眼丁真'
__plugin_usage__ = """输入 !鉴定 !identify !一眼丁真 , 鉴定为: bot
输入 !手动鉴定 结果 -T 标题, 鉴定为: 手动鉴定"""

config = get_driver().config
ua = UserAgent(fallback='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0')

identify = on_command("identify", aliases={"鉴定", "一眼丁真"}, block=True)

ci_parser = ArgumentParser(usage=".customidentify result [--title title] \
                                   [--color hex:color] [--bordercolor hex:bordercolor] [--image url:url]")
ci_parser.add_argument("result")
ci_parser.add_argument("-T", "--title", required=False)
ci_parser.add_argument("-C", "--color", required=False, default="#ffffff")
ci_parser.add_argument("-B", "--border", required=False, default=None)
ci_parser.add_argument("-I", "--image", required=False, default=None)
customidentify = on_shell_command("identify", parser=ci_parser, aliases={"手动鉴定", "自定义鉴定"}, block=True)


@identify.handle()  # .identify
async def _(matcher: Matcher):
    # chosen = os.listdir(f"{os.getcwd()}\\{session.bot.config.STATIC_DIR}\\images\\identify")
    static_dir = config.static_dir
    random.seed(None)
    chosen = os.listdir(f"{static_dir}/images/identify")
    chosen = chosen[random.randint(0, len(chosen) - 1)]
    chosen = "file:///%s" % (os.path.abspath(f"{static_dir}/images/identify/{chosen}"))
    # type="flash",
    # img = MessageSegment(type='image', data={'url': chosen})
    img = MessageSegment.image(file=chosen)
    await matcher.finish(img)


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

        res = None
        try:
            header = {
                "User-Agent": ua.random
            }
            res = requests.get(url, headers=header)
            res.raise_for_status()
        except requests.HTTPError:
            await matcher.finish(f"invalid image url: {res.status_code}")
        except requests.RequestException:
            await matcher.finish("get image failed")
        if int(res.headers['Content-length']) > 1048576:  # 1 MB
            await matcher.finish("image too big")

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
