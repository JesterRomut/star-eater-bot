from PIL import Image


def imgresize(image: Image.Image, target: int) -> Image:
    mul = max(s := image.size) / target
    return image.resize(size=map(lambda x: int(x / mul), s), resample=0, )
