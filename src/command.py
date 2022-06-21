from nonebot.exception import ParserExit
from nonebot.params import ShellCommandArgs
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from functools import partial
from .locale import Localisation, Locale
from nonebot import on_command as _on_command
from nonebot import on_shell_command as _on_shell_command
from nonebot import on_request as _on_request
from nonebot import on_message as _on_message
from nonebot import on_notice as _on_notice

on_command = partial(_on_command, block=True)
on_admin_command = partial(on_command, permission=SUPERUSER)

on_shell_command = partial(_on_shell_command, block=True)
on_admin_shell_command = partial(_on_shell_command, permission=SUPERUSER)

on_request = partial(_on_request, block=True)
on_message = partial(_on_message, block=True)
on_notice = partial(_on_notice, block=True)


async def defaultparserexit(matcher: Matcher, _: ParserExit = ShellCommandArgs(), locale: Localisation = Locale()):
    await matcher.finish(locale["commandlib"]["defaultparserexit"])
