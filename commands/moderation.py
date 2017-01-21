import asyncio

from discord.ext import commands
from utils.mysql import *
from utils.channel_logger import Channel_Logger
from utils.tools import *

class Moderation():
    def __init__(self, bot):
        self.bot = bot
        self.logger = Channel_Logger(bot)

    @commands.command(pass_context=True)
    async def kick(self, ctx, user:discord.Member, *, reason:str=None):
        """Kicks the specified user from the server"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason was specified"
        try:
            await self.bot.kick(user)
        except discord.errors.Forbidden:
            await self.bot.say("I either do not the `Kick Members` permission or my highest role is not higher than that users highest role.")
            return
        #await self.logger.mod_log(ctx.message.server, "`{}` kicked `{}` Reason: `{}`".format(ctx.message.author, user, reason))

    @commands.command(pass_context=True) #aliases don't really work so
    async def kill(self, ctx, user:discord.Member, *, reason:str=None):
        """Kicks the specified user from the server"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason was specified"
        try:
            await self.bot.kick(user)
        except discord.errors.Forbidden:
            await self.bot.say("I either do not the `Kick Members` permission or my highest role is not higher than that users highest role.")
            return
        #await self.logger.mod_log(ctx.message.server, "`{}` kicked `{}` Reason: `{}`".format(ctx.message.author, user, reason))


    @commands.command(pass_context=True)
    async def ban(self, ctx, user:discord.Member, *, reason:str=None):
        """Bans the specified user from the server"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason was specified"
        try:
            await self.bot.ban(user, delete_message_days=0)
        except discord.errors.Forbidden:
            await self.bot.say("I either do not have the `Ban Members` permission or my highest role is not higher than that users highest role.")
            return
        await self.bot.say("Successfully banned `{}`".format(user))
        #await self.logger.mod_log(ctx.message.server, "`{}` banned `{}` Reason: `{}`".format(ctx.message.author, user, reason))

    @commands.command(pass_context=True)
    async def unban(self, ctx, *, username:str):
        """Unbans the user with the specifed name from the server"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        try:
            banlist = await self.bot.get_bans(ctx.message.server)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Ban Members` permission")
            return
        user = discord.utils.get(banlist, name=username)
        if user is None:
            await self.bot.say("No banned user was found with the username of `{}`".format(username))
            return
        await self.bot.unban(ctx.message.server, user)
        await self.bot.say("Successfully unbanned `{}`".format(user))
        #await self.logger.mod_log(ctx.message.server, "`{}` unbanned `{}`".format(ctx.message.author, user))

    @commands.command(pass_context=True)
    async def hackban(self, ctx, id:str, *, reason:str=None):
        """Bans the user with the specified id from the server (Useful if the user isn't on the server yet)"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason was specified"
        try:
            await self.bot.http.ban(id, ctx.message.server.id)
        except discord.errors.HTTPException or discord.errors.NotFound:
            await self.bot.say("No discord user has the id of `{}`".format(id))
            return
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Ban Members` permission")
            return
        banlist = await self.bot.get_bans(ctx.message.server)
        user = discord.utils.get(banlist, id=id)
        await self.bot.say("Successfully banned `{}`".format(user))
        #await self.logger.mod_log(ctx.message.server, "`{}` banned `{}` Reason: `{}`".format(ctx.message.author, user, reason))

    @commands.command(pass_context=True)
    async def banlist(self, ctx):
        """Displays the server's banlist"""
        try:
            banlist = await self.bot.get_bans(ctx.message.server)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Ban Members` permission")
            return
        bancount = len(banlist)
        if bancount == 0:
            banlist = "No users are banned from this server"
        else:
            banlist = ", ".join(map(str, banlist))
        await self.bot.say("Total bans: `{}`\n```{}```".format(bancount, banlist))

    @commands.command(pass_context=True)
    async def mute(self, ctx, user:discord.Member, *, reason:str=None):
        """Mutes the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason was specified"
        mute_role_name = read_data_entry(ctx.message.server.id, "mute-role")
        mute_role = discord.utils.get(ctx.message.server.roles, name=mute_role_name)
        if mute_role is None:
            await self.bot.say("I could not find any role named `{}`".format(mute_role_name))
            return
        try:
            await self.bot.add_roles(user, mute_role)
            await self.bot.say("Successfully muted `{}`".format(user))
            #await self.logger.mod_log(ctx.message.server, "`{}` muted `{}` Reason: `{}`".format(ctx.message.author, user, reason))
        except discord.errors.Forbidden:
            await self.bot.say("I either do not have the `Manage Roles` permission or my highest role is not higher than the `{}` role".format(mute_role_name))

    @commands.command(pass_context=True)
    async def unmute(self, ctx, user:discord.Member):
        """Unmutes the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        mute_role_name = read_data_entry(ctx.message.server.id, "mute-role")
        mute_role = discord.utils.get(ctx.message.server.roles, name=mute_role_name)
        if mute_role is None:
            await self.bot.say("I could not find any role named `{}`".format(mute_role_name))
            return
        try:
            await self.bot.remove_roles(user, mute_role)
            await self.bot.say("Successfully unmuted `{}`".format(user))
            #await self.logger.mod_log(ctx.message.server, "`{}` unmuted `{}`".format(ctx.message.author, user))
        except discord.errors.Forbidden:
            await self.bot.say("I either do not have the `Manage Roles` permission or my highest role is not higher than the `{}` role".format(mute_role_name))

    @commands.command(pass_context=True)
    async def prune(self, ctx, amount:int):
        """Prunes the specified amount of messages"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        try:
            await self.bot.delete_message(ctx.message)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Manage Messages` permission")
            return
        deleted = await self.bot.purge_from(ctx.message.channel, limit=amount)
        deleted_message = await self.bot.say("{} Deleted {} messages".format(ctx.message.author.mention, len(deleted)))
        await asyncio.sleep(10)
        # The try and except pass is so in the event a user prunes again or deletes the
        # prune notification before the bot automatically does it, it will not raise an error
        try:
            await self.bot.delete_message(deleted_message)
        except:
            pass

    """@commands.command(pass_context=True)
    async def clean(self, ctx, amount:int, search_range=50):
        #(!) (WIP) Cleans only the bots messages and the prefixes that has been sent by the user.
    try:
        float(search_range) #lazy check
        search_range = min(int(search_range), 1000)
    except:
        await self.bot.say('`ENTER A DAMN NUMBER. AN INTEGERERERER OR WHATEVER PUT A DIGIT K`')

    await self.bot.delete_message(ctx.message)

    def is_possible_command_invoke(entry):
        valid_call = any(
            entry.content.startswith.(command_prefix) for prefix in [self.config.command_prefix])
        return valid_call and not entry.content[1:2].isspace()

    delete_invokes = True
    delete_all = ctx.message.channel.permissions_for(author).manage_messages or self.config.owner_id == ctx.message.author.id

    def check(ctx.message):
        if is_possible_command_invoke(ctx.message) and delete_invokes:
            return delete_all or ctx.message.author == author
        return message.author == self.bot.user

    if self.bot.user:
        if ctx.message.channel.permissions_for(server.me).manage_messages:
            deleted = await self.bot.purge_from(channel, check=check, limit=search_range, before=ctx.message)
            await bot.say('Cleaned up {} message{}.'.format(len(deleted), 's' * bool(deleted)))"""

    """@commands.command(pass_context=True)
    async def announce(self, ctx, *, announcement:str):
        #Sends an announcement to the announcement channel
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        announcement_channel = discord.utils.get(ctx.message.server.channels, name="announcements")
        if announcement_channel is None:
            await self.bot.say("I could not find a channel named `announcements`")
            return
        msg = make_message_embed(ctx.message.author, 0xCC0000, announcement, useNick=True)
        try:
            await self.bot.send_message(announcement_channel, "@everyone Announcement!", embed=msg)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have permission to send messages in the `announcements` channel")
    """
    @commands.command(pass_context=True)
    async def pin(self, ctx, id:str):
        """Pins the message with the specified ID to the channel"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        try:
            message = await self.bot.get_message(ctx.message.channel, id)
        except discord.errors.NotFound:
            await self.bot.say("No message could be found in this channel with an ID of `{}`".format(id))
            return
        try:
            await self.bot.pin_message(message)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Manage Messages` permission")

    @commands.command(pass_context=True)
    async def unpin(self, ctx, id:str):
        """Unpins the message with the specified ID from the channel"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        pinned_messages = await self.bot.pins_from(ctx.message.channel)
        message = discord.utils.get(pinned_messages, id=id)
        if message is None:
            await self.bot.say("No pinned message could be found in this channel with an ID of `{}`".format(id))
            return
        try:
            await self.bot.unpin_message(message)
            await self.bot.say("Successfully unpinned the message!")
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Manage Messages` permission")

    @commands.command(pass_context=True)
    async def addrole(self, ctx, user:discord.Member, *,  name:str):
        """Adds the specified role to the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("No role with the name of `{}` was found on this server".format(name))
            return
        try:
            await self.bot.add_roles(user, role)
            await self.bot.say("Successfully added the `{}` role to `{}`".format(name, user))
            await self.logger.mod_log(ctx.message.server, "`{}` added the `{}` role to `{}`".format(ctx.message.author, name, user))
        except discord.errors.Forbidden:
            await self.bot.say("I either do not have the `Manage Roles` permission or my highest role isn't higher than the `{}` role".format(name))

    @commands.command(pass_context=True)
    async def removerole(self, ctx, user:discord.Member, *, name:str):
        """Removes the specified role from the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("No role with the name of `{}` was found on this server".format(name))
            return
        try:
            await self.bot.remove_roles(user, role)
            await self.bot.say("Successfully removed the `{}` role from `{}`".format(name, user))
            await self.logger.mod_log(ctx.message.server, "`{}` removed the `{}` role from `{}`".format(ctx.message.author, name, user))
        except discord.errors.Forbidden:
            await self.bot.say("I either do not have the `Manage Roles` permission or my highest role isn't higher than the `{}` role".format(name))

    @commands.command(pass_context=True)
    async def createrole(self, ctx, *, name:str):
        """Creates a role with the specified name"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        try:
            await self.bot.create_role(ctx.message.server, name=name)
            await self.bot.say("Successfully created a role named `{}`".format(name))
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Manage Roles` permission")

    @commands.command(pass_context=True)
    async def deleterole(self, ctx, *, name:str):
        """Deletes the role with the specified name"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("No role was found on this server with the name of `{}`".format(name))
            return
        try:
            await self.bot.delete_role(ctx.message.server, role)
            await self.bot.say("Successfully deleted the role named `{}`".format(name))
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Manage Roles` permission")

    @commands.command(pass_context=True)
    async def editrole(self, ctx, type:str, value:str, *, name:str):
        """Edits a role with the specified name"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("No role was found on this server with the name of `{}`".format(name))
            return
        if type == "color":
            if value != "remove":
                try:
                    color = discord.Color(value=int(value.strip("#"), 16))
                except:
                    await self.bot.say("`{}` is not a valid color. Make sure you are using a hex color! (Ex: #FF0000)".format(value))
                    return
            else:
                color = discord.Color.default()
            try:
                await self.bot.edit_role(ctx.message.server, role, color=color)
                await self.bot.say("Successfully edited the role named `{}`".format(name))
            except discord.errors.Forbidden:
                await self.bot.say("I either do not have the `Manage Roles` permission")
            except discord.errors.NotFound:
                # Don't ask, for some reason if the role is higher than the bot's highest role it returns a NotFound 404 error
                await self.bot.say("That role is higher than my highest role")
        elif type == "permissions":
            try:
                perms = discord.Permissions(permissions=int(value))
            except:
                await self.bot.say("`{}` is not a valid permission number! If you need help finding the permission number, then go to <http://creeperseth.com/discordpermcalc> for a permission calculator!".format(value))
                return
            try:
                await self.bot.edit_role(ctx.message.server, role, permissions=perms)
                await self.bot.say("Successfully edited the role named `{}`".format(name))
            except discord.errors.Forbidden:
                await self.bot.say("I either do not have the `Manage Roles` permission")
            except discord.errors.NotFound:
                await self.bot.say("That role is higher than my highest role")
        elif type == "position":
            try:
                pos = int(value)
            except:
                await self.bot.send_message(ctx.message.channel, "`" + value + "` is not a valid number")
                return
            if pos >= ctx.message.server.me.top_role.position:
                await self.bot.say("That number is not lower than my highest role's position. My highest role's permission is `{}`".format(ctx.message.server.me.top_role.position))
                return
            try:
                if pos <= 0:
                    pos = 1
                await self.bot.move_role(ctx.message.server, role, pos)
                await self.bot.say("Successfully edited the role named `{}`".format(name))
            except discord.errors.Forbidden:
                await self.bot.say("I do not have the `Manage Roles` permission")
            except discord.errors.NotFound:
                await self.bot.say("That role is higher than my highest role")
        elif type == "separate":
            if value.lower() != "true" and value.lower() != "false":
                await self.bot.say("The value must be either `true` or `false`")
                return
            bool = value.lower() == "true"
            try:
                await self.bot.edit_role(ctx.message.server, role, hoist=bool)
                await self.bot.say("Successfully edited the role named `{}`".format(name))
            except discord.errors.Forbidden:
                await self.bot.say("I do not have the `Manage Roles` permission or that role is not lower than my highest role.")
        elif type == "mentionable":
            if value.lower() != "true" and value.lower() != "false":
                await self.bot.say("The value must be either `true` or `false`")
                return
            bool = value.lower() == "true"
            try:
                await self.bot.edit_role(ctx.message.server, role, mentionable=bool)
                await self.bot.say("Successfully edited the role named `{}`".format(name))
            except discord.errors.Forbidden:
                await self.bot.say("I do not have the `Manage Roles` permission")
            except discord.errors.NotFound:
                await self.bot.say("That role is higher than my highest role")
        else:
            await self.bot.say("Invalid type specified, valid types are `color`, `permissions`, `position`, `separate`, and `mentionable`")

    @commands.command(pass_context=True)
    async def renamerole(self, ctx, name:str, newname:str):
        """Renames a role with the specified name, be sure to put double quotes (\") around the name and the new name"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You must have the `{}` role in order to use that command.".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("No role was found on this server with the name of `{}`".format(name))
            return
        try:
            await self.bot.edit_role(ctx.message.server, role, name=newname)
            await self.bot.say("Successfully renamed the `{}` role to `{}`".format(name, newname))
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Manage Roles` permission")
        except discord.errors.NotFound:
            await self.bot.say("That role is higher than my highest role")


def setup(bot):
    bot.add_cog(Moderation(bot))
