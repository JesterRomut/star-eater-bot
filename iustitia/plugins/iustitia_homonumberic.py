from nonebot import on_shell_command
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs, Depends
from nonebot.rule import ArgumentParser, Namespace
from nonebot.adapters import Message
from nonebot.exception import ParserExit
from ..locale import Localisation
from ..iustitia.homonumberic import homonumberic

h_parser = ArgumentParser(usage=".homonumber int:number")
h_parser.add_argument("number", type=int)
homonumber = on_shell_command("homonumber", parser=h_parser,
                              aliases={"homo", "homonumberic", "论证", "恶臭数字", "数字论证", "恶臭数字论证"}, block=True)


@homonumber.handle()
async def _(matcher: Matcher, _: ParserExit = ShellCommandArgs(),
            arg: Message = CommandArg(), locale: Localisation = Depends()):
    arg = arg.extract_plain_text().strip()
    if arg:
        if len(arg) > 125:
            await matcher.finish(locale["parserexit"]["toolong"])
        await matcher.finish(locale["parserexit"]["hasarg"].format(arg=arg))
    await matcher.finish(locale["parserexit"]["hasntarg"])


@homonumber.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs(), locale: Localisation = Depends()):
    if len(str(args.number)) > 9:
        await matcher.finish(locale["toolong"])
    await matcher.finish(homonumberic(args.number))
