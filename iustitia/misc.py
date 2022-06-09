from nonebot.exception import ParserExit
from nonebot.params import ShellCommandArgs
from nonebot.matcher import Matcher


async def defaultparserexit(matcher: Matcher, _: ParserExit = ShellCommandArgs()):
    await matcher.finish("invalid argument")
