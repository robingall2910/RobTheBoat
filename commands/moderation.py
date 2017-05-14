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
            await self.bot.say("No thanks. You need the {} role first.".format(mod_role_name))
            return
        if reason is None:
            reason = "There wasn't a reason given."
        try:
            await self.bot.kick(user)
        except discord.errors.Forbidden:
            await self.bot.say("lol sorry, but I don't have kicking permissions. It'd be really nice to add them to me, or the person has a higher role than me.")
            return
        await self.bot.say("👢'd `{}`".format(user))
        #await self.logger.mod_log(ctx.message.server, "`{}` kicked `{}` Reason: `{}`".format(ctx.message.author, user, reason))

    @commands.command(pass_context=True)
    async def ban(self, ctx, user:discord.Member, *, reason:str=None):
        """Bans the specified user from the server"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("I ain't banning anybody until you have that {} role.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason was specified"
        try:
            await self.bot.ban(user, delete_message_days=0)
        except discord.errors.Forbidden:
            await self.bot.say("I don't have the ban perms myself. Care to add it? If it isn't that, I can't kick them simply because they have a higher role than I do.")
            return
        await self.bot.say("Done! Banned `{}`".format(user))
        #await self.logger.mod_log(ctx.message.server, "`{}` banned `{}` Reason: `{}`".format(ctx.message.author, user, reason))

    @commands.command(pass_context=True)
    async def unban(self, ctx, *, username:str):
        """Unbans the user with the specifed name from the server"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You can unban someone when you have the {} first.".format(mod_role_name))
            return
        try:
            banlist = await self.bot.get_bans(ctx.message.server)
        except discord.errors.Forbidden:
            await self.bot.say("I don't have permission to unban. Well well...")
            return
        user = discord.utils.get(banlist, name=username)
        if user is None:
            await self.bot.say("No username was found under `{}`. They probably aren't banned in the first place??".format(username))
            return
        await self.bot.unban(ctx.message.server, user)
        await self.bot.say("Congratulations! You just unbanned `{}`.".format(user))
        #await self.logger.mod_log(ctx.message.server, "`{}` unbanned `{}`".format(ctx.message.author, user))

    @commands.command(pass_context=True)
    async def hackban(self, ctx, id:str, *, reason:str=None):
        """Bans the user with the specified id from the server (Useful if the user isn't on the server yet)"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("Tryina ban IDs? You need that {} first.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason given."
        try:
            await self.bot.http.ban(id, ctx.message.server.id)
        except discord.errors.HTTPException or discord.errors.NotFound:
            await self.bot.say("No user has the ID of: `{}`".format(id))
            return
        except discord.errors.Forbidden:
            await self.bot.say("Can't ban this ID without having the ban permission.")
            return
        banlist = await self.bot.get_bans(ctx.message.server)
        user = discord.utils.get(banlist, id=id)
        await self.bot.say("Done, banned the ID resolving user `{}`".format(user))
        #await self.logger.mod_log(ctx.message.server, "`{}` banned `{}` Reason: `{}`".format(ctx.message.author, user, reason))

    @commands.command(pass_context=True)
    async def masshban(self, ctx, *, ids:str):
        """Massively bans a group of IDs from the server (Useful if they aren't on the server yet)"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.server.id, name=mod_role_name)
        fuck = asyncio.get_event_loop()
        if not mod:
            await self.bot.say("Now, you're trying to ban several IDs. You need {} first.".format(mod_role_name))
            return
        if reason is None:
            reason = "None"
        try:
            for id in ids:
                await self.bot.http.ban(id, ctx.message.server.id)
        except discord.errors.HTTPException or discord.errors.NotFound:
            await self.bot.say("No one has the ID of `{}`".format(id))
            return
        except discord.errors.Forbidden:
            await self.bot.say("Can't ban these IDs without ban permission, fam")
        banlist = await self.bot.get_bans(ctx.message.server)
        for id in ids:
            user = discord.utils.get(banlist, id=id)
            await self.bot.say("Successfully banned `{}`".format(user))

    @commands.command(pass_context=True)
    async def banlist(self, ctx):
        """Displays the server's banlist"""
        try:
            banlist = await self.bot.get_bans(ctx.message.server)
        except discord.errors.Forbidden:
            await self.bot.say("Boy, you forgot to give me the Ban Members permission so I can actually check.")
            return
        bancount = len(banlist)
        if bancount == 0:
            banlist = "SURPRISE! There's no one banned."
        else:
            banlist = ", ".join(map(str, banlist))
        await self.bot.say("Total bans: `{}`\n```{}```".format(bancount, banlist))

    @commands.command(pass_context=True)
    async def mute(self, ctx, user:discord.Member, *, reason:str=None):
        """Mutes the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("Oi, no muting people until {} exists in my list.".format(mod_role_name))
            return
        if reason is None:
            reason = "No reason was specified"
        mute_role_name = read_data_entry(ctx.message.server.id, "mute-role")
        mute_role = discord.utils.get(ctx.message.server.roles, name=mute_role_name)
        if mute_role is None:
            await self.bot.say("Can't find the role named `{}` for muting lol".format(mute_role_name))
            return
        try:
            await self.bot.add_roles(user, mute_role)
            await self.bot.say("Done! Muted `{}`.".format(user))
            #await self.logger.mod_log(ctx.message.server, "`{}` muted `{}` Reason: `{}`".format(ctx.message.author, user, reason))
        except discord.errors.Forbidden:
            await self.bot.say("I either don't have Manage Roles perm like how I'm supposed to, or that {} role is higher than the highest one I actually have.".format(mute_role_name))

    @commands.command(pass_context=True)
    async def unmute(self, ctx, user:discord.Member):
        """Unmutes the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("Wanna unmute? {} this first. (Add it to your role list if you didn't ;))".format(mod_role_name))
            return
        mute_role_name = read_data_entry(ctx.message.server.id, "mute-role")
        mute_role = discord.utils.get(ctx.message.server.roles, name=mute_role_name)
        if mute_role is None:
            await self.bot.say("Can't find that mute role called `{}`... Does it actually exist?".format(mute_role_name))
            return
        try:
            await self.bot.remove_roles(user, mute_role)
            await self.bot.say("Done! Unmuted `{}`.".format(user))
            #await self.logger.mod_log(ctx.message.server, "`{}` unmuted `{}`".format(ctx.message.author, user))
        except discord.errors.Forbidden:
            await self.bot.say("I either don't have Manage Roles perm like how I'm supposed to, or that {} role is higher than the highest one I actually have.".format(mute_role_name))

    @commands.command(pass_context=True)
    async def prune(self, ctx, amount:int):
        """Prunes the specified amount of messages"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("Not pruning anything until you have that damn role called {}.".format(mod_role_name))
            return
        try:
            await self.bot.delete_message(ctx.message)
        except discord.errors.Forbidden:
            await self.bot.say("I don't have that Manage Messages perm to delete messages fam.")
            return
        deleted = await self.bot.purge_from(ctx.message.channel, limit=amount)
        deleted_message = await self.bot.say("Alright {}, deleted {} messages.".format(ctx.message.author.mention, len(deleted)))
        await asyncio.sleep(10)
        # The try and except pass is so in the event a user prunes again or deletes the
        # prune notification before the bot automatically does it, it will not raise an error
        try:
            await self.bot.delete_message(deleted_message)
        except:
            pass

    @commands.command(pass_context=True)
    async def pruneuser(self, ctx, amount:int, *, user:discord.Member):
        """Prunes the specified amount of messages by a member."""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You're required to have the {} role in order to use the command, sorry.".format(mod_role_name))
            return
        try:
           await self.bot.delete_message(ctx.message)
        except discord.errors.Forbidden:
            await self.bot.say("Well then. I'm missing the Manage Messages permission. Sorry that I can't delete the messages.")
        def the_retarded_fool_tbh(how_could_you_do_this):
            return how_could_you_do_this.user == user
        deleted = await self.bot.purge_from(ctx.message.channel, limit=amount, check=the_retarded_fool_tbh)
        deleted_message = await self.bot.say("{} Deleted {} messages".format(ctx.message.author.mention, len(deleted)))
        # Read the message for the top command you lazy fuck. Or well, I'm the lazy fuck here for not copying.
        try:
            await self.bot.deleted_message(deleted_message)
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
    async def addrole(self, ctx, user:discord.Member, *,  name:str):
        """Adds the specified role to the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You need {} first. I'm not gonna add roles until you do that first...".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("Sorry, I can't find {}. Probably failed you.".format(name))
            return
        try:
            await self.bot.add_roles(user, role)
            await self.bot.say("Done! Added the not-so-magical role `{}` to `{}`".format(name, user))
            #await self.logger.mod_log(ctx.message.server, "`{}` added the `{}` role to `{}`".format(ctx.message.author, name, user))
        except discord.errors.Forbidden:
            await self.bot.say("Hol up fam. I don't have the Manage Roles perm. Give me that first. If that isn't the issue, {} role is higher than the one I have at the top of mine.".format(name))

    @commands.command(pass_context=True)
    async def removerole(self, ctx, user:discord.Member, *, name:str):
        """Removes the specified role from the specified user"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("You needs {} first. No removing until that exists.".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("Can't find {}. Damn, probably failed you again if I did the first time.".format(name))
            return
        try:
            await self.bot.remove_roles(user, role)
            await self.bot.say("Punishment done? Either way, removed `{}` from `{}`".format(name, user))
            #await self.logger.mod_log(ctx.message.server, "`{}` removed the `{}` role from `{}`".format(ctx.message.author, name, user))
        except discord.errors.Forbidden:
            await self.bot.say("Hol up fam. I don't have the Manage Roles perm. Give me that first. If that isn't the issue, {} role is higher than the one I have at the top of mine.".format(name))

    @commands.command(pass_context=True)
    async def createrole(self, ctx, *, name:str):
        """Creates a role with the specified name"""
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(ctx.message.author.roles, name=mod_role_name)
        if not mod:
            await self.bot.say("Add {}. To your role list. No Exceptions.".format(mod_role_name))
            return
        try:
            await self.bot.create_role(ctx.message.server, name=name)
            await self.bot.say("Yeahhhhhhhhhhhhhhhhhhh boiiiiiiiiiiiiiii I just made `{}`.".format(name))
        except discord.errors.Forbidden:
            await self.bot.say("I can't create {} if I don't have the Manage Roles permission lol".format(name))

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
            await self.bot.say("Can't find `{}`. Sometimes, life just gotta be unfair.".format(name))
            return
        try:
            await self.bot.delete_role(ctx.message.server, role)
            await self.bot.say("Lol bye af. Deleted `{}`".format(name))
        except discord.errors.Forbidden:
            await self.bot.say("I can't delet af without the Manage Roles perm")

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
            await self.bot.say("You need {} first fam.".format(mod_role_name))
            return
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("Yeah, I can't find `{}`...".format(name))
            return
        try:
            await self.bot.edit_role(ctx.message.server, role, name=newname)
            await self.bot.say("Woop! Renamed `{}` to `{}`".format(name, newname))
        except discord.errors.Forbidden:
            await self.bot.say("Can't change w/o Manage Roles.")
        except discord.errors.NotFound:
            await self.bot.say("Oi, that role is higher than mine. Unable to edit.")


def setup(bot):
    bot.add_cog(Moderation(bot))
