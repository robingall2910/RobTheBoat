# encoding=utf8

import asyncio
import os
import random
import subprocess
import sys
import time
import traceback

import aiohttp
import psutil
from discord.ext import commands

from utils import checks
from utils.bootstrap import Bootstrap
from utils.buildinfo import *
from utils.channel_logger import Channel_Logger
from utils.config import Config
from utils.logger import log
from utils.mysql import *
from utils.opus_loader import load_opus_lib
from utils.tools import *

#reset
start_time = time.time()

# Initialize the logger first so the colors and shit are setup
log.init()  # Yes I could just use __init__ but I'm dumb

Bootstrap.run_checks()

config = Config()
if config.debug:
    log.enableDebugging()  # pls no flame

bot_triggers = [config.command_prefix, "r.", "hey dragon, ", "hey derg, ", "hey batzz, "]

bot = commands.AutoShardedBot(command_prefix=bot_triggers, description="a bot with no purpose i just memed it since 2015", help_command=discord.ext.commands.DefaultHelpCommand(dm_help=True))
channel_logger = Channel_Logger(bot)
aiosession = aiohttp.ClientSession(loop=bot.loop)
lock_status = config.lock_status

extensions = [
    "commands.fuckery",
    "commands.moderation",
    "commands.configuration",
    "commands.nsfw",
    "commands.music",
    "commands.weather",
    "commands.steam",
    "commands.gw2",
    "commands.lastfm",
    "commands.information",
    "commands.markov",
    "commands.chatlog",
    "commands.hypixel"
]

# Thy changelog
change_log = [
    "you'll never see shit"
]

async def _restart_bot():
    try:
      await aiosession.close()
      await bot.cogs["Music"].disconnect_all_voice_clients()
    except:
       pass
    await subprocess.call([sys.executable, "bot.py"])
    await bot.logout()

async def _shutdown_bot():
    try:
      await bot.cogs["Music"].disconnect_all_voice_clients()
      await aiosession.close()
    except:
       pass
    await bot.logout()

async def set_default_status():
    if not config.enable_default_status:
        return
    type = config.default_status_type
    game = config.default_status_name
    try:
        type = discord.Status(type)
    except:
        type = discord.Status.online
    if game is not None:
        if config.default_status_type == "stream":
            if config.default_status_name is None:
                log.critical("If the status type is set to \"stream\" then the default status game must be specified")
                os._exit(1)
            game = discord.Activity(name=game, url="http://twitch.tv/robingall2910", type=discord.ActivityType.streaming)
        else:
            game = discord.Activity(
                #name="New command invokes are now available!\n\"hey derg\", \"hey dragon\", \"hey batzz\", and \"r.\"! \n\n#BetoSanders2020 #AbramsForGovernor", type=discord.ActivityType.playing)
                name="ryan's are gay (blm btw)", type=discord.ActivityType.playing)
            # pyrawanpmjadbapanwmjamtsatltsadw
        await bot.change_presence(status=type, activity=game)
    else:
        await bot.change_presence(status=type)


@bot.event
async def on_resumed():
    log.info("\nResumed connectivity!")


@bot.event
async def on_ready():
    log.info("\n")
    log.info("Logged in as:\n{}/{}#{}\n----------".format(bot.user.id, bot.user.name, bot.user.discriminator))
    log.info("Bot version: {}\nAuthor(s): {}\nCode name: {}\nBuild date: {}".format(BUILD_VERSION, BUILD_AUTHORS,
                                                                                 BUILD_CODENAME, BUILD_DATE))
    log.debug("Debugging enabled!")
    await set_default_status()
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))
            traceback.print_exc()
    if config.enableOsu:
        log.info("The osu! module has been enabled in the config!")
    if config._dbots_token:
        log.info("Updating DBots Statistics...")
        try:
            r = requests.post("https://discord.bots.gg/api/v1/bots/:{}/stats".format(bot.user.id),
            	              json={"guildCount": len(bot.guilds),
                                    "shardCount": bot.shard_count,
                                    "shardId": bot.shard_id},
                	          headers={"Authorization": config._dbots_token}, timeout=3)
            if r.status_code == 200:
                log.info("Discord Bots Server count updated.")
            elif r.status_code == 401:
                log.error("Woah, unauthorized?")
        except requests.exceptions.Timeout:
            log.error("The server failed to respond in time. Unable to update the bot statistics.")
    if os.path.isdir("data/music"):
        try:
            bot.cogs["Music"].clear_data()
            log.info("The music cache has been cleared!")
        except:
            log.warning("Failed to clear the music cache!")
    #await bot.cogs["Music"].disconnect_all_voice_clients()
    #log.info("Disconnected all voice clients!")
    load_opus_lib()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.DisabledCommand):
        await ctx.send("This command has been disabled")
        return
    if isinstance(error, checks.dev_only):
        await ctx.send("This command can only be ran by the bot developers")
        return
    if isinstance(error, checks.owner_only):
        await ctx.send("This command can only be ran by the bot owner")
        return
    if isinstance(error, checks.not_nsfw_channel):
        await ctx.send("This command can only be ran in NSFW enabled channels.")
        return
    if isinstance(error, checks.not_guild_owner):
        await ctx.send(ctx.channel, "Only the server owner (`{}`) can use this command".format(ctx.guild.owner))
        return
    if isinstance(error, checks.no_permission):
        await ctx.send("You do not have permission to use this command".format(ctx.guild.owner))
        return
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command can only be ran on servers".format(ctx.guild.owner))
        return
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("An error occured while trying to run this command, this is most likely because it was ran in a private message channel. Please try running this command on a guild.")
        return

    #In case the bot failed to send a message to the channel, the try except pass statement is to prevent another error
    try:
        await ctx.send("An error occured while processing the command: `{}`".format(error))
    except:
        pass
    log.error("An error occured while executing the {} command: {}".format(ctx.command.qualified_name, error))


@bot.before_invoke
async def on_command_preprocess(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        server = "Private Message"
    else:
        server = "{}/{}".format(ctx.message.guild.id, ctx.message.guild.name)
    print("[{} at {}] [Command] [{}] [{}/{}]: {}".format(time.strftime("%m/%d/%Y"), time.strftime("%I:%M:%S %p %Z"),
                                                         server, ctx.message.author.id, ctx.message.author,
                                                         ctx.message.content))

@bot.event
async def on_message(message):
    ids = [149688910220361728, 112747894435491840, 188153050471333888]
    serverids = [400012212791541760, 510897834581557251, 142361999538520065, 502979046993559553]
    tfserver = [142361999538520065, 610422741065138179]
    mystupidserver = [704113908276920350]
    #bypassids = [169597963507728384, 117678528220233731, 365274392680333329, 372078453236957185]
    if isinstance(message.author, discord.Member):
        if discord.utils.get(message.author.roles, name="Dragon Ignorance"):
            return
    if message.author.bot:
        return
    if getblacklistentry(message.author.id) is not None and message.clean_content.startswith(config.command_prefix):
        em = discord.Embed(description=None)
        em.title = "Whoops!"
        em.description = "You're blacklisted."
        em.color = 0xFF3346
        em.set_footer(text='if you wish to be removed, find a way to message the bot developers.')
        await message.channel.send(embed=em)
        return
    if message.guild.id in serverids:
        if "<:monika:451965787045888019>" in message.clean_content:
            await message.channel.send("<:monika:451965787045888019> :gay_pride_flag:")
        if re.match(r"(<:monika:451965787045888019>\s*<:Kreygasm:433677270264184833>|<:monika:451965787045888019>\s*<:hyperkreygasm:460417913837322271>)+", message.clean_content):
            await message.channel.send("<:monika:451965787045888019> :gay_pride_flag:")
        if re.match(r"(?=\s*wyoming\s*|\s*kenya\s*)\w+", message.clean_content) is not None:
            await message.channel.send("isn't real")
        if message.author.id in ids:
            if re.match(r"(?=\s*warm\s*|\s*hot\s*|\s*burning\s*)\w+", message.clean_content) is not None:
                await message.channel.send("actually cold")
        if "doki doki isn't weeb" in message.content:
            await message.channel.send("doki doki is weeb")
        if re.match(r"(?=\s*colour)\w+", message.clean_content) is not None or ("colour" or "Colour") in message.clean_content:
            await message.channel.send("color")
    if str(message.channel.id) in getquicklockdownstatus():
        def mod_or_perms(message, **permissions):
            mod_role_name = read_data_entry(message.guild.id, "mod-role")
            mod = discord.utils.get(message.author.roles, name=mod_role_name)
            if mod or permissions and all(
                    getattr(message.channel.permissions_for(message.author), name, None) == value for name, value in
                    permissions.items()):
                return True
            if not message.guild:
                return True
        #if message.author.id in bypassids:
        #    pass
        if mod_or_perms(message, manage_messages=True):
            pass
        else:
            await message.delete()
            log.info(f"Deleted a message due to lockdown from {message.author} in {message.channel}")
            return
    if message.channel.guild.id in tfserver:
        if "unban me" in message.content:
            await message.channel.send("shut up fat")
    if message.channel.guild.id == mystupidserver:
        if re.match(r"(?=\s*nigger)\w+", message.clean_content) is not None or ("nigger" or "Nigger") in message.clean_content:
            await bot.message.delete()
            await message.channel.send(f'{message.author.mention} no n word')
    await bot.process_commands(message)

@bot.command(hidden=True)
@checks.is_dev()
async def debug(ctx, *, shit: str):
    """This is the part where I make 20,000 typos before I get it right"""
    # "what the fuck is with your variable naming" - EJH2
    # seth seriously what the fuck - Robin
    try:
        rebug = eval(shit)
        if asyncio.iscoroutine(rebug):
            rebug = await rebug
        await ctx.send(py.format(rebug))
    except Exception as damnit:
        await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))

@bot.command(hidden=True)
@checks.is_owner()
async def rename(ctx, *, username: str):
    """Renames the bot"""
    await bot.user.edit(name=username)
    await ctx.send("fuck you i changed it to {}".format(username))


@bot.command(hidden=True)
@checks.is_dev()
async def shutdown(ctx):
    """Shuts down the bot"""
    await ctx.send("bye xd")
    log.warning("{} has shut down the bot!".format(ctx.message.author))
    await _shutdown_bot()


@bot.command(hidden=True)
@checks.is_dev()
async def restart(ctx):
    """Restarts the bot"""
    await ctx.send("i'm gonna come back to hit u thx")
    log.warning("{} has restarted the bot!".format(ctx.message.author))
    await _restart_bot()


@bot.command(hidden=True)
@checks.is_owner()
async def setavatar(ctx, *, url: str = None):
    """Changes the bot's avatar"""
    if ctx.message.attachments:
        url = ctx.message.attachments[0]["url"]
    elif url is None:
        await ctx.send("u didn't fuken include a url or a picture retardese")
        return
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiosession.get(url.strip("<>"), timeout=timeout) as image:
            await bot.user.edit(avatar=await image.read())
    except Exception as e:
        await ctx.send("Unable to change avatar: {}".format(e))
    await ctx.send(":eyes:")

@bot.command()
async def notifydev(ctx, *, message:str):
    """Use this if you have bug issues, sends a message to devs"""
    if isinstance(ctx.channel, discord.DMChannel):
        guild = "`Sent via Direct Messages`"
    else:
        guild = "`{}` / `{}`".format(ctx.guild.id, ctx.guild.name)
    msg = make_message_embed(ctx.author, 0xFF0000, message, formatUser=True)
    owner = config.owner_id
    if owner:
        await owner.send("You have received a new message! The user's ID is `{}` Server: {}".format(ctx.author.id, guild), embed=msg)
    for id in config.dev_ids:
        dev = bot.get_user(id)
        if dev:
            await dev.send("You have received a new message! The user's ID is `{}` Server: {}".format(ctx.author.id, guild), embed=msg)
    await ctx.author.send("You've sent in a message to the developers. Your message was: `{}`".format(message))
    await ctx.author.send("Only use this for bug reports. Any other things, like suggestions, you may use .suggestions")
    await ctx.send("Completed the quest.")

@bot.command()
async def suggest(ctx, *, message:str):
    """Sends a suggestion to the main developers"""
    if isinstance(ctx.channel, discord.DMChannel):
        guild = "`Sent via Direct Messages`"
    else:
        guild = "`{}` / `{}`".format(ctx.guild.id, ctx.guild.name)
    msg = make_message_embed(ctx.author, 0xFF0000, message, formatUser=True)
    owner = bot.get_user(config.owner_id)
    if owner:
        await owner.send("You've received a new suggestion! The user's ID is `{}` Server: {}".format(ctx.author.id, guild), embed=msg)
    seth = 169597963507728384
    if seth:
        await seth.send("You've received a new suggestion! The user's ID is `{}` Server: {}".format(ctx.author.id, guild), embed=msg)
        await ctx.author.send("You've successfully sent the suggestion in.")

@bot.command()
@checks.server_mod_or_perms(manage_messages=True)
async def lockdown(ctx, *, mode: str):
    enable = ['true', 'on']
    disable = ['false', 'off']
    if mode in enable:
        try:
            if ctx.channel.id in getquicklockdownstatus():
                await ctx.send("That channel is already locked down!")
            else:
                lockdownchannel(ctx.channel.id, ctx.guild.name, ctx.channel.name)
                await ctx.send("Lockdown is now enabled.")
        except Exception as e:
            await ctx.send("Make sure to check .lockdownstatus, as this may be on!")
            await ctx.send(traceback.format_exc(e))
    elif mode in disable:
        try:
            removelockdownchannel(ctx.channel.id)
            await ctx.send("Lockdown is now disabled.")
        except Exception as e:
            await ctx.send("Make sure to check .lockdownstatus, as this may be on!")
            await ctx.send(traceback.format_exc(e))

@bot.command()
async def lockdownstatus(ctx):
    ls = getlockdowninfo()
    count = len(ls)
    if ls == []:
        ls = "No one is on a lockdown, yay?"
    else:
        ls = "\n".join(ls)
    await ctx.send(xl.format("Total blacklisted users: {}\n\n{}".format(count, ls)))

@bot.command(hidden=True)
@checks.is_dev()
async def blacklist(ctx, id1, *, reason: str):
    """Blacklists a user, BOT OWNER ONLY."""
    if id1 is not int:
        id = int(id1.strip("<@!>"))
    else:
        id = int(id1)
    await ctx.channel.trigger_typing()
    user = bot.get_user(id)
    if user is None:
        await ctx.send("Can't find anyone with `{}`".format(id))
        return
    if getblacklistentry(id) is not None:
        await ctx.send("`{}` is already blacklisted, stop trying.".format(user))
        return
    blacklistuser(id, user.name, user.discriminator, reason)
    await ctx.send("Ok, blacklisted `{}` Reason: `{}`".format(user, reason))
    try:
        await user.send("You've been blacklisted. `{}` Reason: `{}`".format(ctx.message.author, reason))
    except:
        log.debug("Couldn't send a message to a user with an ID of \"{}\"".format(id))

@bot.command(hidden=True)
@checks.is_dev()
async def unblacklist(ctx, id1):
    """Unblacklists a user"""
    if id1 is not int:
        id = int(id1.strip("<@!>"))
    else:
        id = int(id1)
    entry = getblacklistentry(id)
    user = bot.get_user(id)
    if entry is None:
        await ctx.send("No one's found with the ID of `{}`".format(id))
        return
    try:
        unblacklistuser(id)
    except:
        await ctx.send("Can't find the blacklisted user `{}`".format(id))  # Don't ask pls
        return
    await ctx.send("Gave freedom once more to `{}#{}`".format(entry.get("name"), entry.get("discrim")))
    try:
        await user.send("You're unblacklisted. You were unblacklisted by `{}`".format(
                                   ctx.message.author))
    except:
        log.debug("Can't send msg to \"{}\"".format(id))


@bot.command()
async def showblacklist(ctx):
    """Shows the list of users that are blacklisted from the bot"""
    blacklist = getblacklist()
    count = len(blacklist)
    if blacklist == []:
        blacklist = "No blacklisted users! Congratulations."
    else:
        blacklist = "\n".join(blacklist)
    await ctx.send(xl.format("Total blacklisted users: {}\n\n{}".format(count, blacklist)))


@bot.command(hidden=True)
@checks.is_dev()
async def lockstatus(ctx):
    """Toggles the lock on the status"""
    global lock_status
    if lock_status:
        lock_status = False
        await ctx.send("Unlocked.")
    else:
        lock_status = True
        await ctx.send("Locked.")


@bot.command()
async def stream(ctx, *, name: str):
    """Sets the status for the bot stream mode. Advertise your twitch and shit if you'd like."""
    if lock_status:
        await ctx.send("The status is currently locked.")
        return
    name2 = name.replace("@everyone", "").replace("@", "")
    await bot.change_presence(activity=discord.Activity(name=name2.replace("@here", ""), type=discord.ActivityType.streaming, url="https://www.twitch.tv/robingall2910"))
    await ctx.send("Streaming `{}`".format(name2.replace("@here", "")))
    await channel_logger.log_to_channel(":information_source: `{}`/`{}` Changed game name to `{}` with a `streaming` status type".format(ctx.message.author.id, ctx.message.author, name2.replace("@here", "")))



@bot.command()
async def changestatus(ctx, status: str, *, name: str = None):
    """Changes the bot status to a certain status type and game/name/your shitty advertisement/seth's
    life story/your favorite beyonce lyrics and so on"""
    try:
        if name is not None:
            name2 = name.replace("@everyone", "").replace("@", "").replace("@here", "")
        else:
            name2 = None
        if lock_status:
            await ctx.send("Status is locked. Don't try.")
            return
        if name2 is None:
            game = None
        else:
            game = discord.Game(name=name2)
        if status in ("invisible", "offline"):
            await ctx.send("You can not use the status type `{}`".format(status))
            return
        try:
            statustype = discord.Status(status)
        except ValueError:
            await ctx.send(
                "`{}` is not a valid status type, valid status types are `online`, `idle`, `do_not_disturb`, and `dnd`".format(
                    status))
            return
        if name2 is None:
            await bot.change_presence(status=statustype)
            await ctx.send("Changed status type to `{}`".format(statustype))
            log.info("Status changed to {}".format(statustype))
            await channel_logger.log_to_channel(":information_source: `{}`/`{}` has changed the status type to `{}`".format(ctx.message.author.id, ctx.message.author, status))
        else:
            await bot.change_presence(activity=game, status=statustype)
            await ctx.send("Changed game name to `{}` with a(n) `{}` status type".format(name2, statustype))
            log.info("Status changed to {} with name as {}".format(statustype, game))
            await channel_logger.log_to_channel(":information_source: `{}`/`{}` Changed game name to `{}` with a(n) `{}` status type".format(ctx.message.author.id, ctx.message.author, name2.replace("@here", ""), status))
    except:
        await ctx.send(traceback.format_exc())

@bot.command(hidden=True)
@checks.is_dev()
async def terminal(ctx, *, command:str):
    """Spoopy as fuck. Sends a command to the Linux OS."""
    try:
        await ctx.channel.trigger_typing()
        await ctx.send(xl.format(subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(
        )[0].decode("utf-8")))
    except:
        await ctx.send("Well, I broke there.")

@bot.command(hidden=True)
@checks.is_dev()
async def update(ctx):
    """Checks for updates with Git"""
    await ctx.send("Checking for updates...")
    await ctx.channel.trigger_typing()
    try:
        g = subprocess.Popen("git pull".split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode('utf-8')
        if "Already up to date." in g:
            await ctx.send("The bot is up to date!")
        elif "Updating" or "Fast-forward" in g:
            await ctx.send("Update found! Updating, give me a sec...")
            await ctx.channel.trigger_typing()
            await asyncio.sleep(2)
            msg = await ctx.channel.send("Okay, it's done! Do you want to restart?")
            await msg.add_reaction('✔')
            await msg.add_reaction('❌')
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == '✔' and reaction.message == msg
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("You took too long! Canceling operation.")
            else:
                await ctx.send("Restarting!")
                await _restart_bot()
    except:
        await ctx.send(traceback.print_exc())


@bot.command(hidden=True)
@checks.is_dev()
async def uploadfile(ctx, *, path: str):
    """Uploads any file on the system that the bot can access. The hell? My nudes!"""
    await ctx.channel.trigger_typing()
    try:
        await ctx.channel.send(file=discord.File(path))
    except FileNotFoundError:
        await ctx.send("File doesn't exist.")


@bot.command()
async def changelog(ctx):
    """The latest changelog"""
    await ctx.send(
        "For command usages and a list of commands go to https://dragonfire.me/robtheboat/info.html or do `{0}help` "
        "(`{0}help command` for a command usage)\n{1}".format(
            bot.command_prefix, diff.format("\n".join(map(str, change_log)))))


@bot.command()
async def version(ctx):
    """Get the bot's current version"""
    await ctx.send("Bot version: {}\nAuthor(s): {}\nCode name: {}\nBuild date: {}".format(BUILD_VERSION, BUILD_AUTHORS,
                                                                                         BUILD_CODENAME, BUILD_DATE))


@bot.command(hidden=True)
@checks.is_dev()
async def dm(ctx, somethingelse: int, *, message: str):
    """DMs a user"""
    user = bot.get_user(somethingelse)
    owner = bot.get_user(int(config.owner_id))
    msg = make_message_embed(ctx.message.author, 0xE19203, message, formatUser=True)
    try:
        await user.send("You have a new message from the devs!", embed=msg)
        await owner.send(
                               "`{}` has replied to a recent DM with `{}#{}`, an ID of `{}`, and Shard ID `{}`.".format(
                                   ctx.message.author, user.name, user.discriminator, somethingelse, str(bot.shard_id)),
                               embed=make_message_embed(ctx.message.author, 0xCC0000, message))
        for fuck in config.dev_ids:
            try:
                xd = bot.get_user(fuck)
                await xd.send("`{}` has replied to a recent DM with `{}#{}` an ID of `{}`, and Shard ID `{}`.".format(
                              ctx.message.author, user.name, user.discriminator, somethingelse, str(bot.shard_id)),
                              embed=make_message_embed(ctx.message.author, 0xCC0000, message))
            except:
                pass # Don't throw an error when you can't find a dev
    except Exception as e:
        await ctx.send("Error: " + str(e))

@bot.command(hidden=True)
@checks.is_dev()
async def wt(ctx, meme, id:int, *, message: str):
    if meme == "user":
        await ctx.send("Sent the message to ID " + str(id) + ".")
        await bot.get_user(id).send(message)
    elif meme == "channel":
        await ctx.send("Send the message to ID " + str(id) + ".")
        await bot.get_channel(id).send(message)
    else:
        await ctx.send("hey, that isn't a proper type kiddo. either `user` or `channel`. you choose.")


@bot.command()
async def uptime(ctx):
    """Displays how long the bot has been online for"""
    second = time.time() - start_time
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    week, day = divmod(day, 7)
    await ctx.send(
        "I've been online for %d weeks, %d days, %d hours, %d minutes, %d seconds" % (week, day, hour, minute, second))


@bot.command(hidden=True)
@checks.is_dev()
async def reload(ctx, *, extension: str):
    """Reloads an extension"""
    extension = "commands.{}".format(extension)
    if extension in extension:
        await ctx.send("Reloading {}...".format(extension))
        bot.unload_extension(extension)
        bot.load_extension(extension)
        await ctx.send("Reloaded {}!".format(extension))
    else:
        await ctx.send("Extension isn't available.")


@bot.command(hidden=True)
@checks.is_dev()
async def disable(ctx, *, extension: str):
    """Disables an extension"""
    extension = "commands.{}".format(extension)
    if extension in extension:
        await ctx.send("Disabling {}...".format(extension))
        bot.unload_extension(extension)
        await ctx.send("Disabled {}.".format(extension))
    else:
        await ctx.send("Extension isn't available.")


@bot.command(hidden=True)
@checks.is_dev()
async def enable(ctx, *, extension: str):
    """Disables an extension"""
    extension = "commands.{}".format(extension)
    if extension in extension:
        await ctx.send("Loading {}...".format(extension))
        try:
            bot.load_extension(extension)
        except:
            await ctx.send(traceback.print_exc())
        await ctx.send("Enabled {}.".format(extension))
    else:
        await ctx.send("Extension isn't available.")


@bot.command()
async def joinserver(ctx):
    """Sends the bot's OAuth2 link"""
    await ctx.author.send("Want a link to invite me into your server? Here you go. `http://inv.rtb.dragonfire.me`")


@bot.command()
async def invite(ctx):
    """Sends an invite link to the bot's server"""
    await ctx.author.send("Here's the invite for some bot help: `http://discord.gg/fY6JSDf` "
                          "Report with .notifydev if there's an issue with the link.")


@bot.command()
async def ping(ctx):
    """Pings the bot"""
    memes = random.choice(
        ["pinging server...", "hmu on snapchat", "is \"meming\" a thing?", "sometimes I'm scared of furries myself.",
         "You might not understand, but this is gross.", "***0.0 secs***", "hi", "u h h h h h h h h h h h h h",
         "instagram live is lit asf", "SHOW THAT ASS MY NIG",
         "fucking furries...", "fucking maxie", "AAAAAAAAAAAAAAAAAA",
         "why the fuck am I even doing this for you?", "but....", "meh.", "...",
         "Did you really expect something better?", "kek", "I'm killing your dog next time.",
         "Give me a reason to live.", "anyway...", "porn is good.", "I'm edgy.",
         "Damn it seth, why does your internet have to be slow?", "EJ pls.", "Go check out ViralBot today! It's lit.",
         "pink floyd", "how do u feel, how do u feel now, aaaaaaaaaaaaa?", "alan's psychadelic breakfast",
         "Oh.. er.. me flakes.. scrambled eggs.. bacon.. sausages.. tomatoes.. toast.. coffee.. marmalade. I like "
         "marmalade.. yes.. porridge is nice, any cereal.. I like all cereals..", "hi",
         "hi can i get a  uh h hh h h h ", "stop pinging me", "go away nerd", "i secretly love you", "owo", "uwu",
         "google blobs are the best", "lets keep advertising viralbot more!", "napstabot isn't good :^)", "haha net neutrality is dead right? xd",
         "seth be gay sometimes", "no no u", "stop pinging me", "tu eres un gay grande", "xdxdxd", "owu", "do r!neko on Ruby Rose, you'll regret it",
         "404 my ass", "hey! look! i'm not dead!", "quick doctow (・`ω´・)  hand me the defibwiwwatow"])
    topkek = memes
    topkek = memes
    pingms = await ctx.send(topkek)
    ms2 = str(bot.latency)
    if ms2.startswith("0.0"):
        await pingms.edit(content=topkek + " // ***{} ms***".format(ms2[3:][:2]))
    elif ms2.startswith("0."): #for triple digit ping
        await pingms.edit(content=topkek + " // ***{} ms***".format(ms2[2:][:2]))
    elif ms2.startswith("0.00"): #for SINGLE digit ping (thanks google fiber)
        await pingms.edit(content=topkek + " // ***{} ms***".format(ms2[3:][:3]))
    else:
        await pingms.edit(content=topkek + " // ***{} secs***".format(ms2[:3]))

@bot.command()
async def github(ctx):
    """Gives the link to the github repo"""
    await ctx.send(
        "My official github repo can be found here: https://github.com/robingall2910/RobTheBoat")


@bot.command(hidden=True)
async def sneaky(ctx, *, server: str):
    hax = await discord.utils.get(bot.guilds, name=server).system_channel.create_invite()
    await ctx.send("here bitch. " + str(hax))


@bot.command(hidden=True)
async def revokesneaky(ctx, *, invite: str):
    await bot.delete_invite(invite)
    await ctx.send("Deleted invite.")

@bot.command()
@checks.is_dev()
async def editmessage(ctx, id:int, *, newmsg:str):
    """Edits a message sent by the bot"""
    try:
        msg = await bot.get_message(ctx.channel, id)
    except discord.errors.NotFound:
        await ctx.send("Whoops! Can't find the message ID of `{}` in this channel".format(id))
        return
    if msg.author != ctx.guild.me:
        await ctx.send("I didn't send that message... Stop making me edit other people's messages, weirdo.")
        return
    await msg.edit(content=newmsg)
    await ctx.send("owo")


@bot.command(pass_context=True)
async def stats(ctx):
    """Grabs bot statistics."""
    if ctx.message.guild is None:
        musage = psutil.Process().memory_full_info().uss / 1024 ** 2
        uniqueonline = str(sum(1 for m in bot.get_all_members() if m.status != discord.Status.offline))
        sethsfollowers = str(sum(len(s.members) for s in bot.guilds))
        sumupmembers = str(int(str(sethsfollowers)) * int(bot.shard_count))
        sumupuni = str(int(str(uniqueonline)) * int(bot.shard_count))
        em = discord.Embed(description="\u200b", color=ctx.message.guild.me.color)
        em.title = bot.user.name + "'s Help Server"
        em.url = "https://discord.gg/2F69NdA"
        em.set_thumbnail(url=bot.user.avatar_url)
        em.add_field(name='Developers', value='based robin#0052\nscripthead#7988\nLemon#0053', inline=True)
        em.add_field(name='Bot Version', value="v{}".format(BUILD_VERSION), inline=True)
        em.add_field(name='Bot Version Codename', value="\"{}\"".format(BUILD_CODENAME))
        em.add_field(name="Build Date", value=BUILD_DATE, inline=True)
        # em.add_field(name='Shard ID', value="Shard " + str(SID), inline=True)
        em.add_field(name='Voice Connections', value=str(len(bot.voice_clients)) + " servers.", inline=True)
        em.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
        em.add_field(name='Members', value=sumupuni + " ***online*** out of " + sumupmembers, inline=True)
        em.add_field(name='Memory Usage', value='{:.2f} MiB'.format(musage), inline=True)
        await ctx.send(embed=em)
    else:
        musage = psutil.Process().memory_full_info().uss / 1024 ** 2
        uniqueonline = str(sum(1 for m in bot.get_all_members() if m.status != discord.Status.offline))
        sethsfollowers = str(sum(len(s.members) for s in bot.guilds))
        sumupmembers = str(int(str(sethsfollowers)) * int(bot.shard_count))
        sumupuni = str(int(str(uniqueonline)) * int(bot.shard_count))
        em = discord.Embed(description="\u200b")
        em.title = bot.user.name + "'s Help Server"
        em.url = "https://discord.gg/2F69NdA"
        em.set_thumbnail(url=bot.user.avatar_url)
        em.add_field(name='Developers', value='based robin#0052\nscripthead#7988\nLemon#0053', inline=True)
        em.add_field(name='Bot Version', value="v{}".format(BUILD_VERSION), inline=True)
        em.add_field(name='Bot Version Codename', value="\"{}\"".format(BUILD_CODENAME))
        em.add_field(name="Build Date", value=BUILD_DATE, inline=True)
        em.add_field(name='Shard ID', value="Shard " + str(ctx.guild.shard_id), inline=True)
        em.add_field(name='Voice Connections', value=str(len(bot.voice_clients)) + " servers.", inline=True)
        em.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
        em.add_field(name='Members', value=sumupuni + " ***online*** out of " + sumupmembers, inline=True)
        em.add_field(name='Memory Usage', value='{:.2f} MiB'.format(musage), inline=True)
        await ctx.send(embed=em)

@bot.command()
async def top10servers(ctx):
    """Gets the top 10 most populated servers the bot is on for this shard"""
    guilds = []
    for guild in sorted(bot.guilds, key=lambda e: e.member_count, reverse=True)[:10]:
        members = 0
        bots = 0
        total = len(guild.members)
        for member in guild.members:
            if member.bot:
                bots += 1
            else:
                members += 1
        guilds.append("{}: {} members, {} bots ({} total)".format(guild.name, members, bots, total))
    await ctx.send("```{}```".format("\n\n".join(guilds)))


print("doot, starting")
bot.run(config._token)
