from gtts import gTTS, gTTSError
from ..command import on_command
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment
from base64 import b64encode
from io import BytesIO
from ..locale import Localisation, Locale
from asyncio import create_task
from typing import Optional

# _ttsfilename: str = "file.mp3"
# max_workers: int = get_driver().config.executor_max_workers

say = on_command("tts", aliases={"说", "棒读", "捧读", "焚音放送"})


async def _tts(arg) -> Optional[str]:
    # engine = ttsinit()
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
    # engine.setProperty("voice", "en+f4")
    # print(engine.getProperty("voice"))
    # engine.save_to_file(arg, path)
    #engine.runAndWait()
    buff = BytesIO()
    tts = gTTS(arg, lang="zh-CN")
    try:
        tts.write_to_fp(buff)
    except gTTSError:
        return
    return b64encode(buff.getvalue()).decode()


@say.handle()
async def _(matcher: Matcher, arg: Message = CommandArg(), locale: Localisation = Locale()):
    if arg := arg.extract_plain_text():
        if len(arg) > 150:
            await matcher.finish(locale["tts"]["toolong"])
        tts_task = create_task(_tts(arg))
        #with TemporaryDirectory() as d:
        #    path = join(d, _ttsfilename)

        #    with ThreadPoolExecutor(max_workers=20) as executor:
        #        future = executor.submit(_tts, arg=arg, path=path)
        #    # print(listdir(d))
        #    tts = future.result()
        #    while tts.isBusy():
        #        sleep(0.1)
        #    with open(path, "rb") as f:
        #        speech = f.read()
        
        await matcher.finish(
            MessageSegment.record(f"base64://{await tts_task}")
        )
    await matcher.finish(locale["tts"]["absent"])
