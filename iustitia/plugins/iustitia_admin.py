from nonebot import on_shell_command, get_driver, on_command
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs, CommandArg
from nonebot.rule import ArgumentParser, Namespace
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent, GroupMessageEvent, MessageSegment, MessageEvent
from nonebot.adapters.onebot.exception import ActionFailed
from nonebot.adapters import Message
from nonebot.permission import SUPERUSER
from os import path
from shutil import make_archive
from ..misc import defaultparserexit

config = get_driver().config

_globals = {
    "l_audio": lambda f: "file:///{}".format(path.abspath('{s}/audio/{f}'.format(s=config.static_dir, f=f))),
    "l_image": lambda f: "file:///{}".format(path.abspath('{s}/images/{f}'.format(s=config.static_dir, f=f))),
    "ms": MessageSegment,
}

_rn_parser = ArgumentParser(usage=".rename str:name [--group int:group] [--delete]")
_rn_parser.add_argument("name")
_rn_parser.add_argument("-G", "--group", type=int)
_rn_parser.add_argument("-D", "--delete", help="switch delete name", action="store_true")
rename = on_shell_command("rename", parser=_rn_parser, aliases={"改名", }, block=True, permission=SUPERUSER)
rename.append_handler(defaultparserexit)

_w_parser = ArgumentParser(usage=".whisper str:message --user int:user_id / --group int:group_id [--exec]")
_w_parser.add_argument("message")
_w_parser.add_argument("-U", "--user", type=int)
_w_parser.add_argument("-G", "--group", type=int)
_w_parser.add_argument("-E", "--exec", action='store_true')
whisper = on_shell_command("whisper", parser=_w_parser, aliases={"私聊", "私发", }, block=True, permission=SUPERUSER)
whisper.append_handler(defaultparserexit)

leave = on_command("leave", aliases={"退群", "退出", }, permission=SUPERUSER, block=True)

recall = on_command("recall", aliases={"撤回", }, permission=SUPERUSER, block=True)

backup = on_command("backup", aliases={"备份", "生成备份"}, permission=SUPERUSER, block=True)


# b_parser = ArgumentParser(usage=".ban int:banid [--atype str:onebot/guild] [--unban]")
# b_parser.add_argument("banid", type=int)
# b_parser.add_argument("-A", "--atype")
# b_parser.add_argument("-U", "--unban", action='store_false')
# ban = on_shell_command("ban", parser=b_parser, aliases={"禁用", }, block=True, permission=SUPERUSER)

@rename.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent,
            args: Namespace = ShellCommandArgs()):
    if not args.group:
        if isinstance(event, GroupMessageEvent):
            group_id = event.group_id
        else:
            await matcher.finish("no group id")
            return
    else:
        group_id = args.group
    try:
        await bot.set_group_card(group_id=group_id, user_id=event.self_id, card=None if args.delete else args.name)
        logger.info("Renamed as %s in group:%s" % (args.name, group_id))
    except Exception as e:
        await matcher.send("set group card failed")
        raise e
    await matcher.finish("success")


@whisper.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent,
            args: Namespace = ShellCommandArgs()):
    if args.exec:
        try:
            message = eval(args.message, _globals)
        except Exception as e:
            await matcher.finish(str(e))
            return
        # message = list(loc.values())[0]
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

    try:
        await bot.send_msg(
            **{
                "message": message,
                "%s_id" % msgtype: msgid,
            }
        )
    except ActionFailed as e:
        await matcher.send("send message failed %s:%s" % (msgtype, msgid))
        raise e
    else:
        await matcher.finish("successfully sent message to %s:%s" % (msgtype, msgid))


async def _sendmsg(b, msg, u):
    try:
        await b.send_private_msg(message=msg, user_id=u)
    except ActionFailed:
        logger.info("Failed sent message to user:{}".format(u))


@leave.handle()
async def _(bot: Bot, matcher: Matcher, event: MessageEvent,
            arg: Message = CommandArg()):
    if arg := arg.extract_plain_text():
        group_id = arg
    else:
        if isinstance(event, GroupMessageEvent):
            group_id = event.group_id
        else:
            await matcher.finish("must give a group id")
            return

    try:
        group_id = int(group_id)
    except ValueError:
        await matcher.finish("invalid group id")
    else:
        # leave group
        user_id = event.user_id
        try:
            await bot.set_group_leave(group_id=group_id)
        except ActionFailed:
            msg = "Failed leave group:{}".format(group_id)
            logger.info(msg)
            await _sendmsg(bot, msg, user_id)
        else:
            msg = "successfully left group:{}".format(group_id)
            logger.info(msg)
            await _sendmsg(bot, msg, user_id)


@recall.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    if isinstance(event, GroupMessageEvent):
        if reply := event.reply:
            try:
                await bot.delete_msg(message_id=reply.message_id)
                return
            except ActionFailed:
                await matcher.finish("recall failed")


@backup.handle()
async def _(matcher: Matcher):
    await matcher.send("starting backup")
    try:
        make_archive(r"..\..\backup", "zip")
    except Exception as e:
        await matcher.finish("error: {}".format(e))
    else:
        await matcher.finish("success")

# @ban.handle()
# async def _(matcher: Matcher, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent],
#             args: Namespace = ShellCommandArgs(), ):
#     user_id = str(args.banid)
#
#     if args.atype not in ("onebot", "guild",):
#         if isinstance(event, GuildMessageEvent):
#             atype = "guild"
#         else:
#             atype = "onebot"
#     else:
#         atype = args.atype
#
#     with open("memory.json", "r", encoding="UTF-8") as f:
#         memory = loads(f.read())
#
#     perm = memory["perm"][atype]["user"]
#     try:
#         perm[user_id]
#     except KeyError:
#         memory["perm"][atype]["user"][user_id] = {"banned": args.unban}
#     else:
#         memory["perm"][atype]["user"][user_id]["banned"] = args.unban
#
#     with open("memory.json", "w", encoding="UTF-8") as f:
#         f.write(dumps(memory, indent=4))
#
#     await matcher.finish(f"successfully {'' if args.unban else 'un'}banned user:{user_id}")
