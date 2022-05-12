from PIL import Image, ImageDraw, ImageFont, ImageColor
from . import config
from ..imagelib import imgresize
from io import BytesIO
from base64 import b64encode
from os import path


def identify(title: str, desc: str, color: ImageColor,
             border: ImageColor = None, headimage: Image.Image = None) -> str:
    # img process
    with Image.open(f"{config.static_dir}/images/customidentify.JPG") as image:
        font_dir = f"{config.static_dir}/fonts/NotoSansSC-Regular.otf"
        draw = ImageDraw.ImageDraw(image)
        borderw = 5 if border else 0

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

        if title is not None:
            font_title = ImageFont.truetype(font_dir, 100)
            # size = int(2160 / _get_exact_length(desc))
            y = 1250
            draw.text((540, 1050), title, fill=color, anchor="ms", font=font_title,
                      stroke_width=borderw, stroke_fill=border)
        else:
            # size = int(2160 / _get_exact_length(desc))
            y = 1200
        target = 1000

        font_result = ImageFont.truetype(font_dir, _get_size(target))
        draw.text((540, y), desc, fill=color, anchor="ms", font=font_result,
                  stroke_width=borderw, stroke_fill=border)

        # head image
        if headimage is not None:
            with headimage as head:
                pos = (530, 622,)
                headstrip = head.convert('RGBA')
                headstrip = imgresize(headstrip, 600)
                # headstrip = headstrip.resize(size=(int(w / mul), int(h / mul),), reducing_gap=1.01, resample=0, )
                w, h = headstrip.size
                # headstrip.save('headstrip.png')
                image.paste(headstrip,
                            box=(pos[0] - int(w / 2), pos[1] - int(h / 2)),
                            mask=headstrip.split()[3])

        buff = BytesIO()
        image.save(buff, 'jpeg', quality=80)
        return b64encode(buff.getvalue()).decode()


def rua(img: Image.Image) -> str:
    fdir = f"{config.static_dir}/images/rua/"
    isize = [(350, 350), (372, 305), (395, 283), (380, 305), (350, 372)]
    # ipos = [(50, 150), (28, 195), (5, 217), (5, 195), (50, 128)]
    # ipos = [(60, 160), (38, 205), (15, 227), (15, 205), (60, 138)]
    # (235, 335)
    ipos = [(60, 150), (49, 195), (38, 217), (45, 195), (60, 128)]
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
        frame.paste(hand, (0, -20), mask=hand.split()[3])
        mask = frame.split()[3]
        mask = Image.eval(mask, lambda a: 255 if a <= 50 else 0)
        frame = frame.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        frame.paste(255, mask)
        gif.append(frame)

    buff = BytesIO()
    gif[0].save(fp=buff, format="gif", save_all=True, append_images=gif, optimize=True,
                duration=25, loop=0, disposal=2, transparency=255, quality=80)
    return b64encode(buff.getvalue()).decode()
