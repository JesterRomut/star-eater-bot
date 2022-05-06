from PIL import Image
from ..imagelib import imgresize, TransparentAnimatedGifConverter
from nonebot import on_shell_command, get_driver
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.exception import ParserExit
from nonebot.rule import ArgumentParser, Namespace
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from io import BytesIO
from os import path
from base64 import b64encode
from fake_useragent import UserAgent
import requests

__plugin_name__ = '摸摸月亮'
__plugin_usage__ = """输入 !摸摸 图片url 摸摸图片"""

config = get_driver().config

ua = UserAgent(fallback='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0')

r_parser = ArgumentParser(usage=".rua url:url")
r_parser.add_argument("url")
rua = on_shell_command("rua", parser=r_parser, aliases={"pet", "摸摸", "摸", "摸一下", "摸摸月亮", }, block=True)


@rua.handle()
async def _(matcher: Matcher, _: ParserExit = ShellCommandArgs()):
    await matcher.finish("invalid argument")


@rua.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    def _generate_gif(img: Image.Image):
        fdir = f"{config.static_dir}/images/rua/"
        isize = [(350, 350), (372, 305), (395, 283), (380, 305), (350, 372)]
        # ipos = [(50, 150), (28, 195), (5, 217), (5, 195), (50, 128)]
        ipos = [(60, 160), (38, 205), (15, 227), (15, 205), (60, 138)]
        gif = []

        size = 350
        image = Image.new(mode="RGBA", size=(size, size))
        img = imgresize(img, size)
        pos = ((size - img.size[0]) // 2, (size - img.size[1]) // 2)
        image.paste(img, pos, mask=img.split()[3])
        for i in range(5):
            frame = Image.new(mode="RGBA", size=(500, 500))
            hand = Image.open(path.join(fdir, f"{i + 1}.png"))
            hand = hand.convert("RGBA")
            fimage = image.resize(isize[i], reducing_gap=1.01, resample=0, )
            frame.paste(fimage, ipos[i], mask=fimage.split()[3])
            frame.paste(hand, mask=hand.split()[3])
            converter = TransparentAnimatedGifConverter(img_rgba=frame)
            gif.append(converter.process())  # transparency=255,

        buff = BytesIO()
        gif[0].save(fp=buff, format="gif", save_all=True, append_images=gif, optimize=True,
                    duration=25, loop=0, disposal=2, transparency=0, quality=80)
        return b64encode(buff.getvalue()).decode()

    # draedon = Image.open(f"{config.static_dir}/images/Draedon.png")
    # draedon = draedon.convert("RGBA")
    murl = Message(args.url)

    # get url
    for ms in murl:
        if ms.type == "image":
            url = ms.data["url"]
            break
    else:
        url = str(args.url).strip()

    # request
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

    rimage = Image.open(BytesIO(res.content))
    rimage = rimage.convert("RGBA")

    g = _generate_gif(rimage)
    await matcher.finish(MessageSegment.image(f"base64://{g}"))
