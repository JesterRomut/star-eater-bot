from PIL import Image, ImageDraw, ImageFont
from . import config
from .image import imgresize
from io import BytesIO
from base64 import b64encode
from os import listdir, path
from numpy.random import default_rng
from typing import Optional
from functools import partial

_r = default_rng()

_identifypath = "{}/images/identify".format(config.static_dir)
_identifies = listdir(_identifypath)

_fdir = "{}/images/rua/".format(config.static_dir)
_isize = ((350, 350), (372, 305), (395, 283), (380, 305), (350, 372))
# ipos = [(50, 150), (28, 195), (5, 217), (5, 195), (50, 128)]
# ipos = [(60, 160), (38, 205), (15, 227), (15, 205), (60, 138)]
# (235, 335)
_ipos = ((60, 150), (49, 195), (38, 217), (45, 195), (60, 128))
_size = 350


def random_identify() -> str:
    buff = BytesIO()
    with Image.open("{}/{}".format(_identifypath, _r.choice(_identifies))) as image:
        imgresize(image, 500).save(buff, 'jpeg')
    return b64encode(buff.getvalue()).decode()


#
# @jit
async def _get_size(target_width: int, font_dir: str, desc: str) -> int:
    s = 0
    while True:
        f = ImageFont.truetype(font_dir, s)
        if f.getsize(desc)[0] >= target_width:
            break
        s += 1
    return s


async def custom_identify(title: str, desc: str, color: tuple,
                          border: Optional[tuple] = None, headimage: Optional[Image.Image] = None) -> str:
    # img process
    with Image.open("{}/images/customidentify.JPG".format(config.static_dir)) as image:
        font_dir = "{}/fonts/NotoSansSC-Regular.otf".format(config.static_dir)
        draw = ImageDraw.ImageDraw(image)

        addfont = partial(draw.text, fill=color, anchor="ms", stroke_width=5 if border else 0, stroke_fill=border)

        # text
        if title is not None:
            font_title = ImageFont.truetype(font_dir, 100)
            y = 1250
            addfont(xy=(540, 1050), text=title, font=font_title)
        else:
            y = 1200
        font_result = ImageFont.truetype(font_dir, await _get_size(1000, font_dir, desc))
        addfont(xy=(540, y), text=desc, font=font_result)
        # head image
        if headimage is not None:
            with headimage:
                pos = (530, 622,)
                headstrip = headimage.convert('RGBA')
                headstrip = imgresize(headstrip, 600)
                w, h = headstrip.size
                image.paste(headstrip,
                            box=(pos[0] - w // 2, pos[1] - h // 2),
                            mask=headstrip.split()[3])
        buff = BytesIO()
        (image.resize(
            size=map(lambda x: x // 4, image.size),
        )).save(buff, 'jpeg')
        return b64encode(buff.getvalue()).decode()


async def _make_rua_frame(img, idx):
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


async def rua_gif(i: Image.Image) -> str:
    gif = []
    with Image.new(mode="RGBA", size=(_size, _size)) as image:
        with i:
            i = imgresize(i.convert("RGBA"), _size)
            image.paste(i, tuple(map(lambda x: (_size - x) // 2, i.size)), mask=i.split()[3])
            for a in range(5):
                gif.append(await _make_rua_frame(image, a))

    buff = BytesIO()
    gif[0].save(fp=buff, format="gif", save_all=True, append_images=gif, optimize=True,
                duration=25, loop=0, disposal=2, transparency=255, quality=80)
    return b64encode(buff.getvalue()).decode()
