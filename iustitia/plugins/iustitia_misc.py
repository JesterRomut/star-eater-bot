from ..misc import on_command
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from numpy.random import default_rng

_r = default_rng()

reverberation = on_command("reverberation", aliases={"复读", "回声", })
calamityclub = on_command("calamityclub", aliases={"灾厄社", "灾厄社频道", "私货"})


@reverberation.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    if arg := arg.extract_plain_text().strip():
        if len(arg) > 125:
            await matcher.finish("too long message")
        await matcher.finish(arg)
    else:
        await matcher.finish("invalid message")


def _random_insert_seq(lst, seq) -> list:
    inp = iter(lst)
    lst[:] = [inserts[pos] if pos in (
        inserts := dict(zip(
            _r.choice(range(len(lst) + len(seq)), len(seq), replace=False),
            seq))
    ) else next(inp)
              for pos in range(len(lst) + len(seq))]
    return lst


@calamityclub.handle()
async def _(matcher: Matcher):
    raw_url = "https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share" \
              "&inviteCode=1W4oasW&appChannel=share&businessType=9&from=181074&biz=ka&shareSource=5"
    url = "".join(_random_insert_seq(list(raw_url), ["🔥"] * 15))
    res = "是太辣人就来泰拉瑞亚 (灾厄) 社\n" \
          "输入链接加入 QQ 频道【Pony Town灾厄社】: \n\n" \
          f"{url}\n\n" \
          "现在入社领免费泰灾法银批字辈身份, 抢先体验机甲混战和 bug 混战, 还送大怨种代弓老大!"

    await matcher.finish(res)
