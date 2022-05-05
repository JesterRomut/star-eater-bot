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
# from aiocqhttp import MessageSegment
from nonebot.adapters.onebot.v11 import MessageSegment

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

    def _create_identify(name, desc, fcolor, fborder_color, image_url):
        # img process
        with Image.open(f"{config.static_dir}/images/customidentify.JPG") as image:
            font_dir = f"{config.static_dir}/fonts/NotoSansSC-Regular.otf"

            draw = ImageDraw.ImageDraw(image)
            border = 5 if fborder_color else 0

            # text
            def _get_size(target_width):
                s = 0
                while True:
                    f = ImageFont.truetype(font_dir, s)
                    if f.getsize(desc)[0] < target_width:
                        s += 1
                    else:
                        break
                return s

            if name is not None:
                font_title = ImageFont.truetype(font_dir, 100)
                # size = int(2160 / _get_exact_length(desc))
                y = 1250
                draw.text((540, 1050), name, fill=fcolor, anchor="ms", font=font_title,
                          stroke_width=border, stroke_fill=fborder_color)
            else:
                # size = int(2160 / _get_exact_length(desc))
                y = 1200
            target = 1000

            font_result = ImageFont.truetype(font_dir, _get_size(target))
            draw.text((540, y), desc, fill=fcolor, anchor="ms", font=font_result,
                      stroke_width=border, stroke_fill=fborder_color)

            # head image
            if image_url is not None:
                headbyte = BytesIO(image_url.content)
                with Image.open(headbyte) as head:
                    size = 600
                    pos = (530, 622,)
                    headstrip = head.convert('RGBA')
                    w, h = headstrip.size
                    mul = max([w, h]) / size
                    headstrip = headstrip.resize(size=(int(w / mul), int(h / mul),), reducing_gap=1.01, resample=0, )
                    w, h = headstrip.size
                    # headstrip.save('headstrip.png')
                    image.paste(headstrip,
                                box=(pos[0] - int(w / 2), pos[1] - int(h / 2)),
                                mask=headstrip.split()[3])

            buff = BytesIO()
            image.save(buff, 'jpeg')
            return b64encode(buff.getvalue()).decode()

    # request
    if args.image is not None:
        url = str(args.image)
        try:
            header = {
                "User-Agent": ua.random
            }
            headimage = requests.get(url, headers=header)
            headimage.raise_for_status()
        except requests.HTTPError:
            await session.finish(f"invalid image url: {headimage.status_code}")
        except requests.RequestException:
            await session.finish("get image failed")
    try:
        color = ImageColor.getcolor(_hexstrip(args.color), "RGB")
        border_color = ImageColor.getcolor(_hexstrip(args.border), "RGB") if args.border is not None else None
    except ValueError:
        await session.finish("invalid color code")
    if args.title is not None:
        title = args.title
        if title[-2::1] != "丁真":
            title += "丁真"

    await matcher.finish(
        MessageSegment.image(f"base64://{_create_identify(title, result, color, border_color, headimage)}")
    )
