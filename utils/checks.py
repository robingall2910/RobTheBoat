# Thanks Maxie!

import discord

from discord.ext import commands
from utils.config import Config
config = Config()


def is_owner_check(user):
    return user.id == config.owner_id


def is_dev_check(user):
    return user.id in config.dev_ids or is_owner_check(user)


def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message.author))


def is_dev():
    return commands.check(lambda ctx: is_dev_check(ctx.message.author))


def check_perm(ctx, perms):
    msg = ctx.message
    if is_owner_check(msg):
        return True
    channel = msg.channel
    author = msg.author
    resolved = channel.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


def role_or_perm(ctx, check, **perms):
    if check_perm(ctx, perms):
        return True
    channel = ctx.message.channel
    author = ctx.message.author
    if channel.is_private:
        return False
    role = discord.utils.find(check, author.roles)
    return role is not None
