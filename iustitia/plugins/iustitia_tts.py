from tempfile import TemporaryDirectory
from pyttsx3 import init as ttsinit
from ..command import on_command
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment
from base64 import b64encode
from os.path import join
from ..locale import Localisation, Locale

tts = ttsinit()

say = on_command("tts", aliases={"说", "捧读", "焚音放送"})


@say.handle()
async def _(matcher: Matcher, arg: Message = CommandArg(), locale: Localisation = Locale()):
    if arg := arg.extract_plain_text():
        if len(arg) > 50:
            await matcher.finish(locale["tts"]["toolong"])
        with TemporaryDirectory() as d:
            path = join(d, "speech")
            tts.save_to_file(arg, path)
            tts.runAndWait()
            with open(path, "rb") as f:
                speech = b64encode(f.read()).decode()
        await matcher.finish(
            MessageSegment.record("base64://{}".format(speech))
        )
    await matcher.finish(locale["tts"]["absent"])
