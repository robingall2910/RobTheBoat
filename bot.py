# encoding=utf8

import asyncio
import os
import random
import subprocess
import sys
import time

import aiohttp
import psutil
import pyping
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

start_time = time.time()

# Initialize the logger first so the colors and shit are setup
log.init()  # Yes I could just use __init__ but I'm dumb

Bootstrap.run_checks()

config = Config()
if config.debug:
    log.enableDebugging()  # pls no flame

bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or(config.command_prefix), description="A multipurposed bot with a theme for the furry fandom. Contains nsfw, info, weather, music and much more.", pm_help=None)
channel_logger = Channel_Logger(bot)
aiosession = aiohttp.ClientSession(loop=bot.loop)
lock_status = config.lock_status

extensions = ["commands.fuckery", 
              "commands.information", 
              "commands.moderation", 
              "commands.configuration",
              "commands.nsfw", 
              "commands.music", 
              "commands.weather"]

# Thy changelog
change_log = [
    "you'll never see shit"
]

async def _restart_bot():
    try:
      aiosession.close()
      await bot.cogs["Music"].disconnect_all_voice_clients()
    except:
       pass
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
            game = discord.Game(name="distributing porno since 2016")
        await bot.change_presence(status=type, game=game)
    else:
        await bot.change_presence(status=type)


@bot.event
async def on_resumed():
    log.info("\nResumed connectivity!")


@bot.event
async def on_ready():
    print("\n")
    print("Logged in as:\n{}/{}#{}\n----------".format(bot.user.id, bot.user.name, bot.user.discriminator))
    print("Bot version: {}\nAuthor(s): {}\nCode name: {}\nBuild date: {}".format(BUILD_VERSION, BUILD_AUTHORS,
                                                                                 BUILD_CODENAME, BUILD_DATE))
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
        r = requests.post("https://bots.discord.pw/api/bots/{}/stats".format(bot.user.id),
                          json={"server_count": len(bot.guilds)},
                          headers={"Authorization": config._dbots_token})
        if r.status_code == 200:
            log.info("Discord Bots Server count updated.")
        elif r.status_code == 401:
            log.error("Woah, unauthorized?")
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
    if isinstance(message.author, discord.Member):
        if discord.utils.get(message.author.roles, name="Dragon Ignorance"):
            return
    if message.author.bot:
        return
    if getblacklistentry(message.author.id) is not None:
        return

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


"""@bot.command(hidden=True, pass_context=True)
@checks.is_dev()
async def eval(ctx, self):
    await bot.say("Eval enabled. Insert the code you want to evaluate. If you don't want to, type `quit` to exit.")
    if death = await bot.wait_for_message(author=ctx.message.author, content=quit):
        return
    else:
        to_the_death = await bot.wait_for_message(author=ctx.message.author)
        try:
            ethan_makes_me_suffer = eval(to_the_death)
            if asyncio.iscoroutine(ethan_makes_me_suffer):
                ethan_makes_me_suffer = await ethan_makes_me_suffer
            await bot.say(py.format(ethan_makes_me_suffer))
        except Exception as why_do_you_do_this_to_me:
            await bot.say(py.format("{}: {}".format(type(why_do_you_do_this_to_me).__name__, why_do_you_do_this_to_me)))
            """


@bot.command(hidden=True)
@checks.is_owner()
async def rename(ctx, *, name: str):
    """Renames the bot"""
    await bot.edit_profile(username=name)
    await ctx.send("fuck you i changed it to {}".format(name))


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
        with aiohttp.Timeout(10):
            async with aiosession.get(url.strip("<>")) as image:
                await bot.user.edit(avatar=await image.read())
    except Exception as e:
        await ctx.send("Unable to change avatar: {}".format(e))
    await ctx.send(":eyes:")

@bot.command()
async def notifydev(ctx, *, message:str):
    """Sends a message to the developers"""
    if isinstance(ctx.channel, discord.DMChannel):
        guild = "`Sent via Direct Messages`"
    else:
        guild = "`{}` / `{}`".format(ctx.guild.id, ctx.guild.name)
    msg = make_message_embed(ctx.author, 0xFF0000, message, formatUser=True)
    owner = bot.get_user(config.owner_id)
    if owner:
        await owner.send("You have received a new message! The user's ID is `{}` Server: {}".format(ctx.author.id, guild), embed=msg)
    for id in config.dev_ids:
        dev = bot.get_user(id)
        if dev:
            await dev.send("You have received a new message! The user's ID is `{}` Server: {}".format(ctx.author.id, guild), embed=msg)
    await ctx.author.send("You've sent in a message to the developers. Your message was: `{}`".format(message))
    await ctx.send("Completed the quest.")


@bot.command(hidden=True)
@checks.is_dev()
async def blacklist(ctx, id: int, *, reason: str):
    """Blacklists a user, BOT OWNER ONLY."""
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
        await user.send("You've been blacklisted. We aren't supposed to talk. Sorry. `{}` Reason: `{}`".format(
                                   ctx.message.author, reason))
    except:
        log.debug("Couldn't send a message to a user with an ID of \"{}\"".format(id))
        # await channel_logger.log_to_channel(":warning: `{}` blacklisted `{}`/`{}` Reason: `{}`".format
        # (ctx.message.author, id, user, reason))


@bot.command(hidden=True)
@checks.is_dev()
async def unblacklist(ctx, id: int):
    """Unblacklists a user"""
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
        await user.send("You're unblacklisted you titty. You were unblacklisted by `{}`".format(
                                   ctx.message.author))
    except:
        log.debug("Can't send msg to \"{}\"".format(id))
        # await channel_logger.log_to_channel(":warning: `{}` unblacklisted `{}`/`{}#{}`".format(ctx.message.author,
        # id, entry.get("name"), entry.get("discrim")))


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
@checks.is_owner()
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
    await bot.change_presence(game=discord.Game(name=name, type=1, url="https://www.twitch.tv/robingall2910"))
    await ctx.send("Streaming `{}`".format(name))
    await channel_logger.log_to_channel(":information_source: `{}`/`{}` Changed game name to `{}` with a `streaming` status type".format(ctx.message.author.id, ctx.message.author, name))


@bot.command()
async def changestatus(ctx, status: str, *, name: str = None):
    """Changes the bot status to a certain status type and game/name/your shitty advertisement/seth's
    life story/your favorite beyonce lyrics and so on"""
    if lock_status:
        await ctx.send("Status is locked. Don't try.")
        return
    game = None
    if status == "invisible" or status == "offline":
        await ctx.send("You can not use the status type `{}`".format(status))
        return
    try:
        statustype = discord.Status(status)
    except ValueError:
        await ctx.send(
            "`{}` is not a valid status type, valid status types are `online`, `idle`, `do_not_disurb`, and `dnd`".format(
                status))
        return
    if name != "":
        game = discord.Game(name=name)
    await bot.change_presence(game=game, status=statustype)
    if name is not None:
        await ctx.send("Changed game name to `{}` with a(n) `{}` status type".format(name, status))
        await channel_logger.log_to_channel(":information_source: `{}`/`{}` Changed game name to `{}` with a(n) `{}` status type".format(ctx.message.author.id, ctx.message.author, name, status))
    else:
        await ctx.send("Changed status type to `{}`".format(status))
        await channel_logger.log_to_channel(":information_source: `{}`/`{}` has changed the status type to `{}`".format(ctx.message.author.id, ctx.message.author, status))


@bot.command(hidden=True)
@checks.is_dev()
async def terminal(ctx, *, command:str):
    """Spoopy as fuck. Sends a command to the Linux OS."""
    try:
        await ctx.channel.trigger_typing()
        await ctx.send(xl.format(subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(
        )[0].decode("ascii")))
    except:
        await ctx.send("Well, I broke there.")



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
    owner = bot.get_user(config.owner_id)
    msg = make_message_embed(ctx.message.author, 0xE19203, message, formatUser=True)
    try:
        await user.send("You have a new message from the devs!", embed=msg)
        await owner.send(
                               "`{}` has replied to a recent DM with `{}#{}`, an ID of `{}`, and Shard ID `{}`.".format(
                                   ctx.message.author, user.name, user.discriminator, somethingelse, str(bot.shard_id)),
                               embed=make_message_embed(ctx.message.author, 0xCC0000, message))
        for fuck in config.dev_ids:
            xd = bot.get_user(fuck)
            await xd.send("`{}` has replied to a recent DM with `{}#{}` an ID of `{}`, and Shard ID `{}`.".format(
                          ctx.message.author, user.name, user.discriminator, somethingelse, str(bot.shard_id)),
                          embed=make_message_embed(ctx.message.author, 0xCC0000, message))
    except Exception as e:
        await ctx.send("Error: " + str(e))

"""
@bot.command(hidden=True)
@checks.is_dev()
async def wt(ctx, id: str, *, message: str):
    await ctx.send("Sent the message to ID " + id + ".")
    await bot.send_message(discord.Object(id=id), message) # There's no good rw replacement
"""


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
        bot.load_extension(extension)
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
    await ctx.author.send("Here's the invite for some bot help: `https://discord.gg/vvAKvaG` "
                          "Report with {}notifydev if there's an issue with the link.".format(
                              bot.command_prefix))


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
         "marmalade.. yes.. porridge is nice, any cereal.. I like all cereals..",
         "so, how's was trumps bullshit on executive orders?", "don't sign the I-407 in the airport", "hi",
         "hi can i get a  uh h hh h h h ", "stop pinging me", "go away nerd", "i secretly love you", "owo", "uwu",
         "google blobs are the best", "lets keep advertising viralbot more!", "napstabot isn't good :^)", "haha net neutrality is dead right? xd"])
    topkek = memes
    pingms = await ctx.send(topkek)
    r = pyping.ping('dragonfire.me')
    # await bot.edit_message(pingms, topkek + " // ***{} ms***".format(str(ping)[3:][:3]))
    await pingms.edit(content=topkek + " // ***{} ms***".format(r.avg_rtt))


@bot.command()
async def website(ctx):
    """Gives the link to the bot docs"""
    await ctx.send(
        "My official website can be found here: https://dragonfire.me/robtheboat/info.html - Please be aware its outdated.")


@bot.command()
async def github(ctx):
    """Gives the link to the github repo"""
    await ctx.send(
        "My official github repo can be found here: https://github.com/robingall2910/RobTheBoat - This is running the ***dragon*** branch.")


@bot.command(hidden=True)
async def sneaky(ctx, *, server: str):
    hax = await discord.utils.get(bot.guilds, name=server).create_invite()
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
        em.add_field(name='Creators', value='based robin#0052 and ZeroEpoch1969#0051', inline=True)
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
        em.add_field(name='Creators', value='based robin#0052 and ZeroEpoch1969#0051', inline=True)
        em.add_field(name='Bot Version', value="v{}".format(BUILD_VERSION), inline=True)
        em.add_field(name='Bot Version Codename', value="\"{}\"".format(BUILD_CODENAME))
        em.add_field(name="Build Date", value=BUILD_DATE, inline=True)
        # em.add_field(name='Shard ID', value="Shard " + str(SID), inline=True)
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
