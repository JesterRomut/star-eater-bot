from PIL import Image


def resize(image: Image.Image, target):
    w, h = image.size
    mul = max([w, h]) / target
    return image.resize(size=(int(w / mul), int(h / mul),), reducing_gap=1.01, resample=0, )