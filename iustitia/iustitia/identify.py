from PIL import Image, ImageDraw, ImageFont, ImageColor
from . import config
from ..imagelib import imgresize
from io import BytesIO
from base64 import b64encode


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
