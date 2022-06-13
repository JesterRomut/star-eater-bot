from PIL import Image, ImageDraw, ImageFont
from . import config
from .image import imgresize
from io import BytesIO
from base64 import b64encode
from os import path, scandir, DirEntry
from numpy.random import default_rng
from typing import Optional
from functools import partial
from concurrent.futures import ThreadPoolExecutor

_r = default_rng()

_identifypath = f"{config.static_dir}/images/identify"

_fdir = f"{config.static_dir}/images/rua/"
_isize = ((350, 350), (372, 305), (395, 283), (380, 305), (350, 372))
_ipos = ((60, 150), (49, 195), (38, 217), (45, 195), (60, 128))
_size = 350


async def _random_file() -> DirEntry:
    n, res = 0, None
    for file in scandir(_identifypath):
        n += 1
        if _r.uniform(0, n) < 1:
            res = file
    return res


async def random_identify() -> str:
    return path.abspath((await _random_file()).path)


#
# @jit
def _get_size(target_width: int, font_dir: str, desc: str) -> int:
    s = 0
    while True:
        f = ImageFont.truetype(font_dir, s)
        if f.getsize(desc)[0] >= target_width:
            break
        s += 1
    return s


def _custom_identify(title: str, desc: str, color: tuple,
                     border: Optional[tuple] = None, headimage: Optional[Image.Image] = None) -> str:
    font_dir = f"{config.static_dir}/fonts/NotoSansSC-Regular.otf"
    # img process
    with Image.open(f"{config.static_dir}/images/customidentify.JPG") as image:
        draw = ImageDraw.ImageDraw(image)

        addfont = partial(draw.text, fill=color, anchor="ms", stroke_width=5 if border else 0, stroke_fill=border)

        # text
        if title is not None:
            font_title = ImageFont.truetype(font_dir, 100)
            y = 1250
            addfont(xy=(540, 1050), text=title, font=font_title)
        else:
            y = 1200

        font_result = ImageFont.truetype(font_dir, _get_size(1000, font_dir, desc))
        addfont(xy=(540, y), text=desc, font=font_result)

        # head image
        if headimage:
            # headimage = Image.open(BytesIO(headimage.content))
            with headimage:
                pos = (530, 622,)
                headstrip = headimage.convert('RGBA')
                headstrip = imgresize(headstrip, 600)
                w, h = headstrip.size
                image.paste(headstrip,
                            box=(pos[0] - w // 2, pos[1] - h // 2),
                            mask=headstrip.split()[3])

        buff = BytesIO()
        image.save(buff, 'jpeg')
        return b64encode(buff.getvalue()).decode()


async def custom_identify(title: str, desc: str, color: tuple,
                          border: Optional[tuple] = None, headimage: Optional[Image.Image] = None) -> str:
    with ThreadPoolExecutor(max_workers=100) as executor:
        future = executor.submit(_custom_identify,
                                 title=title,
                                 desc=desc,
                                 color=color,
                                 border=border,
                                 headimage=headimage)
    return future.result()


def _make_rua_frame(img, idx) -> Image.Image:
    with Image.new(mode="RGBA", size=(500, 500)) as frame:
        with Image.open(path.join(_fdir, "{}.png".format(idx + 1))) as hand:
            hand = hand.convert("RGBA")
            fimage = img.resize(_isize[idx], reducing_gap=1.01, resample=0, )
            frame.paste(fimage, _ipos[idx], mask=fimage.split()[3])
            frame.paste(hand, (0, -20), mask=hand.split()[3])
        mask = Image.eval(frame.split()[3], lambda m: 255 if m <= 50 else 0)
        frame = frame.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        frame.paste(255, mask)
        return frame


def rua_gif(i: Image.Image) -> str:
    with Image.new(mode="RGBA", size=(_size, _size)) as image:
        i = imgresize(i.convert("RGBA"), _size)
        image.paste(i, ((_size - i.size[0])//2, (_size - i.size[1])//2), mask=i.split()[3])

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(_make_rua_frame, img=image, idx=a) for a in range(5)]

    gif = [f.result() for f in futures]

    buff = BytesIO()
    gif[0].save(fp=buff, format="gif", save_all=True, append_images=gif, optimize=True,
                duration=25, loop=0, disposal=2, transparency=255, quality=80)

    return b64encode(buff.getvalue()).decode()
