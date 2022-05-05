from nonebot import on_shell_command, get_driver, on_command
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs, CommandArg
from nonebot.rule import ArgumentParser, Namespace
from nonebot.exception import ParserExit
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.exception import ApiNotAvailable, ActionFailed
from nonebot.adapters import Message
from nonebot.permission import SUPERUSER
from typing import Union
import os

config = get_driver().config

rn_parser = ArgumentParser(usage=".rename str:name [--group int:group] [--delete]")
rn_parser.add_argument("name")
rn_parser.add_argument("-G", "--group", type=int)
rn_parser.add_argument("-D", "--delete", help="switch delete name", action="store_true")
rename = on_shell_command("rename", parser=rn_parser, aliases={"改名", }, block=True, permission=SUPERUSER)

w_parser = ArgumentParser(usage=".whisper str:message --user int:user_id / --group int:group_id [--exec]")
w_parser.add_argument("message")
w_parser.add_argument("-U", "--user", type=int)
w_parser.add_argument("-G", "--group", type=int)
w_parser.add_argument("-E", "--exec", action='store_true')
whisper = on_shell_command("whisper", parser=w_parser, aliases={"私聊", "私发", }, block=True, permission=SUPERUSER)

leave = on_command("leave", aliases={"退群", "退出", }, permission=SUPERUSER, block=True)


@rename.handle()
async def _(matcher: Matcher, _: ParserExit = ShellCommandArgs()):
    await matcher.finish("invalid argument")


@rename.handle()
async def _(matcher: Matcher, bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent],
            args: Namespace = ShellCommandArgs()):
    user_id = event.self_id
    if not args.group:
        if isinstance(event, PrivateMessageEvent):
            await matcher.finish("no group id")
            return
        else:
            group_id = event.group_id
    else:
        group_id = args.group
    try:
        await bot.set_group_card(group_id=group_id, user_id=user_id, card=None if args.delete else args.name)
        logger.info("Rename as %s in group:%s" % (args.name, group_id))
    except Exception as e:
        await matcher.send("set group card failed")
        raise e
    await matcher.finish("success")


@whisper.handle()
async def _(matcher: Matcher, _: ParserExit = ShellCommandArgs()):
    await matcher.finish("invalid argument")


@whisper.handle()
async def _(matcher: Matcher, bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent],
            args: Namespace = ShellCommandArgs()):
    if args.exec:
        loc = {}
        glo = {
            "l_audio": lambda f: f"file:///{os.path.abspath(f'{config.static_dir}/audio/{f}')}",
            "l_image": lambda f: f"file:///{os.path.abspath(f'{config.static_dir}/images/{f}')}",
            "ms": MessageSegment,
        }
        try:
            exec(args.message, glo, loc)
        except Exception as e:
            await session.finish(str(e))
        message = list(loc.values())[0]
    else:
        message = str(args.message)
    msgtype = None
    msgid = None

    if args.user is not None:
        msgtype = "user"
        msgid = args.user
    elif args.group is not None:
        msgtype = "group"
        msgid = args.group
    else:
        if isinstance(event, PrivateMessageEvent):
            # private reverberation
            msgtype = "user"
            msgid = event.user_id
        else:
            await matcher.finish("must give a target id and type")

    param = {
        "message": message,
        "%s_id" % msgtype: msgid,
    }

    try:
        await bot.send_msg(**param)
    except (ApiNotAvailable, ActionFailed) as e:
        await matcher.send("send message failed %s:%s" % (msgtype, msgid))
        raise e
    else:
        await matcher.finish("successfully sent message to %s:%s" % (msgtype, msgid))


async def _leavegroup(bot, group_id, user_id):
    async def _sendmsg(b, msg, u):
        try:
            await b.send_private_msg(message=msg, user_id=u)
        except (ApiNotAvailable, ActionFailed):
            pass

    try:
        await bot.set_group_leave(group_id=group_id)
    except (ApiNotAvailable, ActionFailed):
        logger.info(f"Failed leave group:{group_id}")
        await _sendmsg(bot, f"failed leave group:{group_id}", user_id)
    else:
        logger.info(f"Left group:{group_id}")
        await _sendmsg(bot, f"successfully left group:{group_id}", user_id)


@leave.handle()
async def _(bot: Bot, matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent],
            arg: Message = CommandArg()):
    user_id = event.user_id
    arg = str(arg).strip()
    if not arg:
        if isinstance(event, GroupMessageEvent):
            group_id = event.group_id
        else:
            await matcher.finish("must give a group id")
            return
    else:
        group_id = arg
    try:
        group_id = int(group_id)
    except ValueError:
        await matcher.finish("invalid group id")
    else:
        await _leavegroup(bot, group_id, user_id)



