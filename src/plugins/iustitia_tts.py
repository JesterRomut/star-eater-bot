from tempfile import TemporaryDirectory
from pyttsx3 import init as ttsinit
from ..command import on_command
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from base64 import b64encode
from os.path import join
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from ..locale import Localisation, Locale

_ttsfilename = "file.mp3"

say = on_command("tts", aliases={"说", "棒读", "捧读", "焚音放送"})


def _tts(arg, path):
    engine = ttsinit()
    # _voices = engine.getProperty('voices')
    # vid = _voices[0].id
    # for voice in _voices:
    #     print(voice.id, voice.languages)
    #     if b"\x05zh" in voice.languages:
    #         vid = voice.id
    #         logger.info(f"Match voice: {vid}")
    #         break
    # else:
    #     logger.warning("Could not find a chinese speaking voice.")
    engine.setProperty("voice", "en+f4")
    # print(engine.getProperty("voice"))
    engine.save_to_file(arg, path)
    engine.runAndWait()
    return engine


@say.handle()
async def _(matcher: Matcher, arg: Message = CommandArg(), locale: Localisation = Locale()):
    if arg := arg.extract_plain_text():
        if len(arg) > 150:
            await matcher.finish(locale["tts"]["toolong"])
        with TemporaryDirectory() as d:
            path = join(d, _ttsfilename)

            with ThreadPoolExecutor(max_workers=20) as executor:
                future = executor.submit(_tts, arg=arg, path=path)
            # print(listdir(d))
            tts = future.result()
            while tts.isBusy():
                sleep(0.1)
            with open(path, "rb") as f:
                speech = f.read()
        await matcher.finish(
            MessageSegment.record(f"base64://{b64encode(speech).decode()}")
        )
    await matcher.finish(locale["tts"]["absent"])
