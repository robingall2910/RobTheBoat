import asyncio
import os
import aiohttp
import time
import sys
import subprocess
import psutil
import random

start_time = time.time()

# Initialize the logger first so the colors and shit are setup
from utils.logger import log
log.init() # Yes I could just use __init__ but I'm dumb

from utils.bootstrap import Bootstrap
Bootstrap.run_checks()

from utils import checks

from discord.ext import commands
from utils.config import Config
from utils.tools import *
from utils.channel_logger import Channel_Logger
from utils.mysql import *
from utils.buildinfo import *
from utils.opus_loader import load_opus_lib
#import isinstance as sethisreallytrulyaprettygayboy - sethpls
from utils.sharding import shard_id
from utils.sharding import shard_count

config = Config()
if config.debug:
    log.enableDebugging() # pls no flame
bot = commands.Bot(command_prefix=config.command_prefix, description="A multi-purpose furry dragon bot that includes music", shard_id=shard_id, shard_count=shard_count, pm_help=True)
channel_logger = Channel_Logger(bot)
aiosession = aiohttp.ClientSession(loop=bot.loop)
lock_status = config.lock_status

extensions = ["commands.fuckery", "commands.information", "commands.moderation", "commands.configuration", "commands.nsfw", "commands.music"]

# Thy changelog
change_log = [
    "Version increment, more bugs fixed/removed"
]

async def _restart_bot():
    await bot.logout()
    subprocess.call([sys.executable, "bot.py"])


async def _shutdown_bot():
    try:
      aiosession.close()
      await bot.cogs["Music"].disconnect_all_voice_clients()
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
            game = discord.Game(name=game, url="http://twitch.tv/robingall2910", type=1)
        else:
            game = discord.Game(name="Shard {} of {} // {} guilds on this shard".format(str(shard_id), str(shard_count), len(bot.servers)))
        await bot.change_presence(status=type, game=game)
    else:
        await bot.change_presence(status=type)

@bot.event
async def on_resumed():
    log.info("\nReconnected to discord!")



@bot.event
async def on_ready():
    print("Logged in as:\n{}/{}#{}\n----------".format(bot.user.id, bot.user.name, bot.user.discriminator))
    print("Bot version: {}\nAuthor(s): {}\nCode name: {}\nBuild date: {}".format(BUILD_VERSION, BUILD_AUTHORS, BUILD_CODENAME, BUILD_DATE))
    log.debug("Debugging enabled!")
    await set_default_status()
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))
    if config.enableMal:
        try:
            bot.load_extension("commands.myanimelist")
            log.info("The MyAnimeList module has been enabled!")
        except Exception as e:
            log.error("Failed to load the MyAnimeList module\n{}: {}".format(type(e).__name__, e))
    if config.enableOsu:
        log.info("The osu! module has been enabled in the config!")
    if config._dbots_token:
        log.info("Updating DBots Statistics...")
        r = requests.post("https://bots.discord.pw/api/bots/{}/stats".format(bot.user.id), json={"shard_id": shard_id, "shard_count": shard_count, "server_count":len(bot.servers)}, headers={"Authorization":config._dbots_token})
        if r.status_code == "200":
            log.info("Discord Bots Server count updated.")
        elif r.status_code == "401":
            log.error("Woah, unauthorized?")
    load_opus_lib()

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        return
    if ctx.message.channel.is_private:
        await bot.send_message(ctx.message.channel, "Command borked. If this is in a PM, do it in the server. Try to report this with {}notifydev.".format(config.command_prefix))
        return

    # In case the bot failed to send a message to the channel, the try except pass statement is to prevent another error
    try:
        await bot.send_message(ctx.message.channel, error)
    except:
        pass
    log.error("An error occured while executing the command named {}: {}".format(ctx.command.qualified_name, error))

@bot.event
async def on_command(command, ctx):
    if ctx.message.channel.is_private:
        server = "Private Message"
    else:
        server = "{}/{}".format(ctx.message.server.id, ctx.message.server.name)
    print("[Command] [{}] [{}/{}]: {}".format(server, ctx.message.author.id, ctx.message.author, ctx.message.content))

@bot.event
async def on_message(message):
    if discord.Member is type(message.author):
        if discord.utils.get(message.author.roles, name="Dragon Ignorance"):
            return

    if getblacklistentry(message.author.id) is not None:
        return

    await bot.process_commands(message)
"""
@bot.event
async def on_server_update(before:discord.Server, after:discord.Server):
    if before.name != after.name:
        await channel_logger.mod_log(after, "Server name was changed from `{}` to `{}`".format(before.name, after.name))
    if before.region != after.region:
        await channel_logger.mod_log(after, "Server region was changed from `{}` to `{}`".format(before.region, after.region))
    if before.afk_channel != after.afk_channel:
        await channel_logger.Channel_logg.mod_log(after, "Server afk channel was changed from `{}` to `{}`".format(before.afk_channel.name, after.afk_channel.name))
    if before.afk_timeout != after.afk_timeout:
        await channel_logger.mod_log(after, "Server afk timeout was changed from `{}` seconds to `{}` seconds".format(before.afk_timeout, after.afk_timeout))
    if before.icon != after.icon:
        await channel_logger.mod_log(after, "Server icon was changed from {} to {}".format(before.icon_url, after.icon_url))
    if before.mfa_level != after.mfa_level:
        if after.mfa_level == 0:
            mfa = "enabled"
        else:
            mfa = "disabled"
        await channel_logger.mod_log(after, "Server two-factor authentication requirement has been `{}`".format(mfa))
    if before.verification_level != after.verification_level:
        await channel_logger.mod_log(after, "Server verification level was changed from `{}` to `{}`".format(before.verification_level, after.verification_level))
    if before.owner != after.owner:
        await channel_logger.mod_log(after, "Server ownership was transferred from `{}` to `{}`".format(before.owner, after.owner))
"""
@bot.event
async def on_member_join(member:discord.Member):
    join_message = read_data_entry(member.server.id, "join-message")
    if join_message is not None:
        join_message = join_message.replace("!USER!", member.mention).replace("!SERVER!", member.server.name)
    join_leave_channel_id = read_data_entry(member.server.id, "join-leave-channel")
    if join_leave_channel_id is not None:
        join_leave_channel = discord.utils.get(member.server.channels, id=join_leave_channel_id)
        if join_leave_channel is None:
            update_data_entry(member.server.id, "join-leave-channel", None)
    else:
        join_leave_channel = None
    join_role_id = read_data_entry(member.server.id, "join-role")
    if join_role_id is not None:
        join_role = discord.utils.get(member.server.roles, id=join_role_id)
        if join_role is None:
            update_data_entry(member.server.id, "join-role", None)
    else:
        join_role = None
    if join_leave_channel is not None and join_message is not None:
        try:
            await bot.send_message(join_leave_channel, join_message)
        except:
            pass
    if join_role is not None:
        try:
            await bot.add_roles(member, join_role)
        except:
            None

@bot.event
async def on_member_remove(member:discord.Member):
    leave_message = read_data_entry(member.server.id, "leave-message")
    if leave_message is not None:
        leave_message = leave_message.replace("!USER!", member.mention).replace("!SERVER!", member.server.name)
    join_leave_channel_id = read_data_entry(member.server.id, "join-leave-channel")
    if join_leave_channel_id is not None:
        join_leave_channel = discord.utils.get(member.server.channels, id=join_leave_channel_id)
        if join_leave_channel is None:
            update_data_entry(member.server.id, "join-leave-channel", None)
    else:
        join_leave_channel = None
    if join_leave_channel is not None and leave_message is not None:
        try:
            await bot.send_message(join_leave_channel, leave_message)
        except:
            pass

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def debug(ctx, *, shit:str):
    """This is the part where I make 20,000 typos before I get it right"""
    # "what the fuck is with your variable naming" - EJH2
    # seth seriously what the fuck - Robin
    try:
        rebug = eval(shit)
        if asyncio.iscoroutine(rebug):
            rebug = await rebug
        await bot.say(py.format(rebug))
    except Exception as damnit:
        await bot.say(py.format("{}: {}".format(type(damnit).__name__, damnit)))

@bot.command(hidden=True)
@checks.is_owner()
async def rename(*, name:str):
    """Renames the bot"""
    await bot.edit_profile(username=name)
    await bot.say("Changed my name to {}".format(name))

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def shutdown(ctx):
    """Shuts down the bot"""
    await bot.say("Goodbye.")
    log.warning("{} has shut down the bot!".format(ctx.message.author))
    await _shutdown_bot()

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def restart(ctx):
    """Restarts the bot"""
    await bot.say("Restarting, I'll come back.")
    log.warning("{} has restarted the bot!".format(ctx.message.author))
    await _restart_bot()

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def setavatar(ctx, *, url:str=None):
    """Changes the bot's avatar"""
    if ctx.message.attachments:
        url = ctx.message.attachments[0]["url"]
    elif url is None:
        await bot.say("u didn't fuken include a url or a picture retardese")
        return
    try:
        with aiohttp.Timeout(10):
            async with aiosession.get(url.strip("<>")) as image:
                await bot.edit_profile(avatar=await image.read())
    except Exception as e:
        await bot.say("Unable to change avatar: {}".format(e))
    await bot.say(":eyes:")

@bot.command(pass_context=True)
async def notifydev(ctx, *, message:str):
    """Sends a message to the developers"""
    if ctx.message.channel.is_private:
        server = "`Sent via PM, not a server`"
    else:
        server = "`{}` / `{}`".format(ctx.message.server.id, ctx.message.server.name)
    msg = make_message_embed(ctx.message.author, 0xCC0000, message, formatUser=True)
    await bot.send_message(discord.User(id=config.owner_id), "You have received a new message! The user's ID is `{}` Server: {} Shard: {}".format(ctx.message.author.id, server, str(shard_id)), embed=msg)
    for id in config.dev_ids:
        await bot.send_message(discord.User(id=id), "You have received a new message! The user's ID is `{}` Server: {} Shard: {}".format(ctx.message.author.id, server, str(shard_id)), embed=msg)
    await bot.send_message(ctx.message.author, "You've sent a message to the developers. The following message contained: `{}`".format(message))
    await bot.say("Message sent!")

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def blacklist(ctx, id:str, *, reason:str):
    """Blacklists a user"""
    await bot.send_typing(ctx.message.channel)
    user = discord.utils.get(list(bot.get_all_members()), id=id)
    if user is None:
        await bot.say("Could not find a user with an id of `{}`".format(id))
        return
    if getblacklistentry(id) != None:
        await bot.say("`{}` is already blacklisted".format(user))
        return
    blacklistuser(id, user.name, user.discriminator, reason)
    await bot.say("Blacklisted `{}` Reason: `{}`".format(user, reason))
    try:
        await bot.send_message(user, "You have been blacklisted from the bot by `{}` Reason: `{}`".format(ctx.message.author, reason))
    except:
        log.debug("Couldn't send a message to a user with an ID of \"{}\"".format(id))
    #await channel_logger.log_to_channel(":warning: `{}` blacklisted `{}`/`{}` Reason: `{}`".format(ctx.message.author, id, user, reason))

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def unblacklist(ctx, id:str):
    """Unblacklists a user"""
    entry = getblacklistentry(id)
    if entry is None:
        await bot.say("No blacklisted user can be found with an id of `{}`".format(id))
        return
    try:
        unblacklistuser(id)
    except:
        await bot.say("No blacklisted user can be found with an id of `{}`".format(id)) # Don't ask pls
        return
    await bot.say("Successfully unblacklisted `{}#{}`".format(entry.get("name"), entry.get("discrim")))
    try:
        await bot.send_message(discord.User(id=id), "You have been unblacklisted from the bot by `{}`".format(ctx.message.author))
    except:
        log.debug("Couldn't send a message to a user with an ID of \"{}\"".format(id))
    #await channel_logger.log_to_channel(":warning: `{}` unblacklisted `{}`/`{}#{}`".format(ctx.message.author, id, entry.get("name"), entry.get("discrim")))

@bot.command()
async def showblacklist():
    """Shows the list of users that are blacklisted from the bot"""
    blacklist = getblacklist()
    count = len(blacklist)
    if blacklist == []:
        blacklist = "No blacklisted users! Congratulations."
    else:
        blacklist = "\n".join(blacklist)
    await bot.say(xl.format("Total blacklisted users: {}\n\n{}".format(count, blacklist)))

@bot.command()
async def commands_used(self):
    """Gives info on how many commands have been used."""
    msg = []
    if dict(self.bot.commands_used):
        for k, v in dict(self.bot.commands_used).items():
            msg.append(str(k), str(v) + "uses")
    else:
        msg = [("None", "No commands seemed to have been run yet!")]
    """if self.bot.embeddable:
            await self.bot.say(content="", embed=discord.Embed(title="Commands Run:", description=util.neatly(
                entries=msg, colors="autohotkey")))
            return"""
    #await self.bot.say(util.neatly(entries=msg, colors="autohotkey"))
    await self.bot.say("Commands Ran: " + msg)
    #its not neat but damn you EJH2

@bot.command(hidden=True)
@checks.is_owner()
async def lockstatus():
    """Toggles the lock on the status"""
    global lock_status
    if lock_status:
        lock_status = False
        await bot.say("The status has been unlocked")
    else:
        lock_status = True
        await bot.say("The status has been locked")

@bot.command(pass_context=True)
async def stream(ctx, *, name:str):
    """Sets the status for the bot stream mode. Advertise your twitch and shit if you'd like."""
    if lock_status:
        await bot.say("The status is currently locked.")
        return
    await bot.change_presence(game=discord.Game(name=name, type=1, url="https://www.twitch.tv/robingall2910"))
    await bot.say("Now streaming `{}`".format(name))

@bot.command(pass_context=True)
async def changestatus(ctx, status:str, *, name:str=None):
    """Changes the bot status to a certain status type and game/name/your shitty advertisement/seth's life story/your favorite beyonce lyrics and so on"""
    if lock_status:
        await bot.say("The status is currently locked")
        return
    game = None
    if status == "invisible" or status == "offline":
        await bot.say("You can not use the status type `{}`".format(status))
        return
    try:
        statustype = discord.Status(status)
    except ValueError:
        await bot.say("`{}` is not a valid status type, valid status types are `online`, `idle`, `do_not_disurb`, and `dnd`".format(status))
        return
    if name != "":
        game = discord.Game(name=name)
    await bot.change_presence(game=game, status=statustype)
    if name is not None:
        await bot.say("Changed game name to `{}` with a(n) `{}` status type".format(name, status))
        #await channel_logger.log_to_channel(":information_source: `{}`/`{}` Changed game name to `{}` with a(n) `{}` status type".format(ctx.message.author.id, ctx.message.author, name, status))
    else:
        await bot.say("Changed status type to `{}`".format(status))
        #await channel_logger.log_to_channel(":information_source: `{}`/`{}` has changed the status type to `{}`".format(ctx.message.author.id, ctx.message.author, status))

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def terminal(ctx, *, command:str):
    """Runs terminal commands and shows the output via a message. Oooh spoopy!"""
    try:
        await bot.send_typing(ctx.message.channel)
        await bot.say(xl.format(os.popen(command).read()))
    except:
        await bot.say("Unable to send the command, too long?")

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def uploadfile(ctx, *, path:str):
    """Uploads any file on the system. What is this hackery?"""
    await bot.send_typing(ctx.message.channel)
    try:
        await bot.send_file(ctx.message.channel, path)
    except FileNotFoundError:
        await bot.say("File doesn't exist.")

@bot.command()
async def changelog():
    """The latest changelog"""
    await bot.say("For command usages and a list of commands go to https://dragonfire.me/robtheboat/info.html or do `{0}help` (`{0}help command` for a command usage)\n{1}".format(bot.command_prefix, diff.format("\n".join(map(str, change_log)))))

@bot.command()
async def version():
    """Get the bot's current version"""
    await bot.say("Bot version: {}\nAuthor(s): {}\nCode name: {}\nBuild date: {}".format(BUILD_VERSION, BUILD_AUTHORS, BUILD_CODENAME, BUILD_DATE))

@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def dm(ctx, id:str, *, message:str):
    """DMs a user"""
    msg = make_message_embed(ctx.message.author, 0xE19203, message, formatUser=True)
    try:
        await bot.send_message(discord.User(id=id), "You got a message from the developers!", embed=msg)
        await bot.say("Message sent!")
    except:
        await bot.say("Failed to send the message.")

@bot.command()
async def uptime():
    """Displays how long the bot has been online for"""
    second = time.time() - start_time
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    week, day = divmod(day, 7)
    await bot.say("I've been online for %d weeks, %d days, %d hours, %d minutes, %d seconds" % (week, day, hour, minute, second))

@bot.command(hidden=True)
@checks.is_dev()
async def reload(*, extension:str):
    """Reloads an extension"""
    extension = "commands.{}".format(extension)
    if extension in extension:
        await bot.say("Reloading {}...".format(extension))
        bot.unload_extension(extension)
        bot.load_extension(extension)
        await bot.say("Reloaded {}!".format(extension))
    else:
        await bot.say("Extension isn't available.")

@bot.command(hidden=True)
@checks.is_dev()
async def disable(*, extension:str):
	"""Disables an extension"""
	extension = "commands.{}".format(extension)
	if extension in extension:
		await bot.say("Disabling {}...".format(extension))
		bot.unload_exension(extension)
		await bot.say("Disabled {}.".format(extension))
	else:
		await bot.say("Extension isn't available.")

@bot.command(pass_context=True)
async def joinserver(ctx):
    """Sends the bot's OAuth2 link"""
    await bot.send_message(ctx.message.author, "Want a link to invite me into your server? Here you go. `http://inv.rtb.dragonfire.me`")

@bot.command(pass_context=True)
async def invite(ctx):
    """Sends an invite link to the bot's server"""
    await bot.send_message(ctx.message.author, "Here's the invite for some bot help: `https://discord.gg/zU8mcKd` Report with {}notifydev if there's an issue with the link.".format(bot.command_prefix))

@bot.command(pass_context=True)
async def ping(ctx):
    """Pings the bot"""
    pingtime = time.time()
    memes = random.choice(["pinging server...", "hmu on snapchat", "is \"meming\" a thing?", "sometimes I'm scared of furries myself.", "You might not understand, but this is gross.", "***0.0 secs***", "hi", "u h h h h h h h h h h h h h", "instagram live is lit asf", "SHOW THAT ASS MY NIG",
                               "fucking furries...", "fucking maxie", "AAAAAAAAAAAAAAAAAA",
                               "why the fuck am I even doing this for you?", "but....", "meh.", "...",
                               "Did you really expect something better?", "kek", "I'm killing your dog next time.",
                               "Give me a reason to live.", "anyway...", "porn is good.", "I'm edgy.", "Damn it seth, why does your internet have to be slow?", "EJ pls.", "Go check out ViralBot today! It's lit.", "pink floyd", "how do u feel, how do u feel now, aaaaaaaaaaaaa?", "alan's psychadelic breakfast", "Oh.. er.. me flakes.. scrambled eggs.. bacon.. sausages.. tomatoes.. toast.. coffee.. marmalade. I like marmalade.. yes.. porridge is nice, any cereal.. I like all cereals.."
                               "so, how's was trumps bullshit on executive orders?", "don't sign the I-407 in the airport"])
    topkek = memes
    pingms = await bot.send_message(ctx.message.channel, topkek)
    ping = time.time() - pingtime
    await bot.edit_message(pingms, topkek + " // ***%.01f secs***" % (ping))

@bot.command()
async def website():
    """Gives the link to the bot docs"""
    await bot.say("My official website can be found here: https://dragonfire.me/robtheboat/info.html")

@bot.command()
async def github():
    """Gives the link to the github repo"""
    await bot.say("My official github repo can be found here: https://github.com/robingall2910/RobTheBoat")

@bot.command(hidden=True)
async def sneaky(*, server: str):
    hax = bot.create_invite(discord.utils.find(lambda m: m.name == server, bot.servers))
    await bot.say(hax)

@bot.command()
async def stats(self):
    """Grabs bot statistics."""
    SID = shard_id
    musage = psutil.Process().memory_full_info().uss / 1024**2
    uniqueonline = str(sum(1 for m in bot.get_all_members() if m.status != discord.Status.offline))
    sethsfollowers = str(sum(len(s.members) for s in bot.servers))
    sumitup = str(int(len(bot.servers)) * int(shard_count))
    sumupmembers = str(sethsfollowers * int(shard_count))
    sumupuni = str(uniqueonline * int(shard_count))
    em = discord.Embed(description="\u200b")
    em.title = bot.user.name + "'s Help Server"
    em.url = "https://discord.gg/qBj2ZRT"
    em.set_thumbnail(url=self.bot.user.avatar_url)
    em.add_field(name='Created by', value='Robin#0052 and Seth#9790')
    em.add_field(name='Bot Version', value=BUILD_VERSION)
    em.add_field(name="Build Date", value=BUILD_DATE)
    em.add_field(name='Shard ID', value="Shard " + str(SID))
    em.add_field(name='Voice Connections', value=str(len(self.bot.voice_clients)) + " servers.")
    em.add_field(name='Servers', value=sumitup)
    em.add_field(name='Members', value=sumupmembers + "/" + sumupuni)
    em.add_field(name="Shard Server Count", value=len(self.bot.servers))
    em.add_field(name='Memory Usage', value='{:.2f} MiB - Shard {} only'.format(musage, str(SID)))
    await bot.say(embed=em)

bot.run(config._token)
