from PIL import Image


def imgresize(image: Image.Image, target: int) -> Image:
    mul = max(s := image.size) / target
    return image.resize(size=(int(s[0] / mul), int(s[1] / mul)), resample=0, )
