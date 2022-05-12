import random

from nonebot import on_command, get_driver
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Message

from ujson import loads

config = get_driver().config
with open(f"{config.static_dir}/storage/answers.json", encoding="UTF-8") as f:
    answers = loads(f.read())

answer = on_command("answer", aliases={"答案之书", "答案", "翻看答案", }, block=True)


@answer.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = str(arg).strip()
    if not arg:
        await matcher.finish("答案: 你问题呢？")
    if len(arg) > 125:
        await matcher.finish("答案: 太长了, 下一个")
    random.seed(None)
    chosen = answers[random.choice(list(answers))]["answer"]
    await matcher.finish(f"事件: {arg}\n答案: {chosen}")
