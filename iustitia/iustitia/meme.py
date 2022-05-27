from PIL import Image, ImageDraw, ImageFont
from . import config
from .image import imgresize
from io import BytesIO
from base64 import b64encode
from os import listdir, path
from numpy.random import default_rng
from typing import Optional

_r = default_rng()

_identifypath = f"{config.static_dir}/images/identify"
_identifies = listdir(_identifypath)


def random_identify() -> str:
    chosen = _r.choice(_identifies)
    chosen = path.abspath(f"{_identifypath}/{chosen}")
    return chosen


#
# @jit
def _get_size(target_width: int, font_dir: str, desc: str) -> int:
    s = 0
    while True:
        f = ImageFont.truetype(font_dir, s)
        if f.getsize(desc)[0] < target_width:
            s += 1
        else:
            break
    return s


def custom_identify(title: str, desc: str, color: tuple,
                    border: Optional[tuple] = None, headimage: Optional[Image.Image] = None) -> str:
    # img process
    with Image.open(f"{config.static_dir}/images/customidentify.JPG") as image:
        font_dir = f"{config.static_dir}/fonts/NotoSansSC-Regular.otf"
        draw = ImageDraw.ImageDraw(image)
        borderw = 5 if border else 0

        # text

        if title is not None:
            font_title = ImageFont.truetype(font_dir, 100)
            y = 1250
            draw.text((540, 1050), title, fill=color, anchor="ms", font=font_title,
                      stroke_width=borderw, stroke_fill=border)
        else:
            y = 1200
        font_result = ImageFont.truetype(font_dir, _get_size(1000, font_dir, desc))
        draw.text((540, y), desc, fill=color, anchor="ms", font=font_result,
                  stroke_width=borderw, stroke_fill=border)
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
        image.save(buff, 'jpeg', quality=80)
        return b64encode(buff.getvalue()).decode()


def rua_gif(i: Image.Image) -> str:
    fdir = f"{config.static_dir}/images/rua/"
    isize = [(350, 350), (372, 305), (395, 283), (380, 305), (350, 372)]
    # ipos = [(50, 150), (28, 195), (5, 217), (5, 195), (50, 128)]
    # ipos = [(60, 160), (38, 205), (15, 227), (15, 205), (60, 138)]
    # (235, 335)
    ipos = [(60, 150), (49, 195), (38, 217), (45, 195), (60, 128)]
    gif = []

    size = 350
    with Image.new(mode="RGBA", size=(size, size)) as image:
        with i:
            img = i.convert("RGBA")
            img = imgresize(img, size)
            pos = ((size - img.size[0]) // 2, (size - img.size[1]) // 2)
            image.paste(img, pos, mask=img.split()[3])
            for a in range(5):
                with Image.new(mode="RGBA", size=(500, 500)) as frame:
                    with Image.open(path.join(fdir, f"{a + 1}.png")) as hand:
                        hand = hand.convert("RGBA")
                        fimage = image.resize(isize[a], reducing_gap=1.01, resample=0, )
                        frame.paste(fimage, ipos[a], mask=fimage.split()[3])
                        frame.paste(hand, (0, -20), mask=hand.split()[3])
                    mask = frame.split()[3]
                    mask = Image.eval(mask, lambda m: 255 if m <= 50 else 0)
                    frame = frame.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                    frame.paste(255, mask)
                    gif.append(frame)

    buff = BytesIO()
    gif[0].save(fp=buff, format="gif", save_all=True, append_images=gif, optimize=True,
                duration=25, loop=0, disposal=2, transparency=255, quality=80)
    return b64encode(buff.getvalue()).decode()
