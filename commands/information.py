import os
import socket
import datetime
import time
import traceback

from discord.ext import commands
from utils.tools import *
from utils.logger import log
from utils.unicode import *
from utils.config import Config
config = Config()

halloween = datetime(2019, 10, 31)
christmas = datetime(2019, 12, 25)
newyear = datetime(2020, 1, 1)

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def id(self, ctx, user:discord.User=None):
        """Gets your ID or if you @mention a user it gets their id"""
        if user is None:
            await ctx.send("Your ID is `{}`".format(ctx.message.author.id))
        else:
            await ctx.send("{}'s ID is `{}`".format(user, user.id))

    @commands.guild_only()
    @commands.command()
    async def serverinfo(self, ctx):
        """Gets information on the current server"""
        guild = ctx.guild
        human_count = len([member for member in guild.members if not member.bot])
        bot_count = len(([member for member in guild.members if member.bot]))
        timeout_times = {60:"1 minute", 300:"5 minutes", 900:"15 minutes", 1800:"30 minutes", 3600:"1 hour"}
        fields = {"ID":guild.id, "Created on":format_time(guild.created_at), "Region":guild.region, "Member Count ({} total)".format(len(guild.members)):"{} humans, {} bots".format(human_count, bot_count), "Channel Count ({} total)".format(len(guild.channels)):"{} text, {} voice".format(len(guild.text_channels), len(guild.voice_channels)), "Role Count":len(guild.roles), "Owner":guild.owner, "Owner ID":guild.owner_id, "AFK Channel":guild.afk_channel, "AFK Timeout":timeout_times[guild.afk_timeout], "Verification Level":str(ctx.guild.verification_level).capitalize().replace("High", tableflip).replace("Extreme", doubleflip), "2FA Enabled":convert_to_bool(guild.mfa_level)}
        embed = make_list_embed(fields)
        embed.title = guild.name
        if ctx.me.color is not None:
            embed.color = ctx.me.color
        else:
            embed.color = 0xff0000
        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def userinfo(self, ctx, *, user:discord.Member=None):
        """Gets your information or the information of the specified user"""
        try:
            if user is None:
                user = ctx.author
            game = None
            if user.activity:
                game = user.activity.name
            voice_channel = None
            self_mute = False
            self_deaf = False
            server_mute = False
            server_deaf = False
            if user.voice:
                voice_channel = user.voice.channel
                self_mute = user.voice.self_mute
                self_deaf = user.voice.self_deaf
                server_mute = user.voice.mute
                server_deaf = user.voice.deaf
            fields = {"ID":user.id, "Bot Account":user.bot, "Created on":format_time(user.created_at), "Status":user.status, "Role Count":len(user.roles), "Joined on":format_time(user.joined_at), "Nickname":user.nick, "Voice Channel":voice_channel, "Self Muted":self_mute, "Self Deafened":self_deaf, "Server Muted":server_mute, "Server Deafened":server_deaf}
            embed = make_list_embed(fields)
            embed.set_footer(text="Requested by {}".format(ctx.author), icon_url=ctx.author.avatar_url)
            embed.title = str(user)
            embed.color = user.color
            embed.set_thumbnail(url=get_avatar(user))
            embed.footer = ctx.author
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(traceback.format_exc())

    @commands.command()
    async def roleinfo(self, ctx, *, name:str):
        """Gets information on a role, warning, it might take up the entire screen"""
        role = discord.utils.get(ctx.guild.roles, name=name)
        if role is None:
            await ctx.send("`{}` isn't real. Or is it?".format(name))
            return
        color = role.color
        if color == discord.Color(value=0x000000):
            color = "None"
        count = len([member for member in ctx.guild.members if discord.utils.get(member.roles, name=role.name)])
        perms = role.permissions
        fields = {
            "Position":role.position,
            "User count":count,
            "Mentionable":role.mentionable,
            "Display seperately":role.hoist,"Add reactions":perms.add_reactions,
            "Administrator":perms.administrator,
            "Attach files":perms.attach_files,
            "Ban members":perms.ban_members,
            "Change nickname":perms.change_nickname,
            "Connect":perms.connect,
            "Create instant invites":perms.create_instant_invite,
            "Deafen members":perms.deafen_members,
            "Embed links":perms.embed_links,
            "External emojis":perms.external_emojis,
            "Kick members":perms.kick_members,
            "Manage channels":perms.manage_channels,
            "Manage emojis":perms.manage_emojis,
            "Manage guild":perms.manage_guild,
            "Manage messages":perms.manage_messages,
            "Manage nicknames":perms.manage_nicknames,
            "Manage roles":perms.manage_roles,
            "Manage webhooks":perms.manage_webhooks,
            "Mention everyone":perms.mention_everyone,
            "Move members":perms.move_members,
            "Mute members":perms.mute_members,
            "Read message history":perms.read_message_history,
            "Read messages":perms.read_messages,
            "Send messages":perms.send_messages,
            "Send TTS messages":perms.send_tts_messages,
            "Speak":perms.speak,
            "Use voice activation":perms.use_voice_activation,
            "View audit logs":perms.view_audit_log
        }
        embed = make_list_embed(fields)
        embed.set_footer(text="Requested by {}".format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.title = "{} - {}".format(role.name, role.id)
        if color is None:
            embed.color = None
        else:
            embed.color = color
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, *, user:discord.User=None):
        """Gets your avatar url or the avatar url of the specified user"""
        if user is None:
            user = ctx.message.author
        if not user.avatar_url:
            avatar_url = user.default_avatar_url
        else:
            avatar_url = user.avatar_url
        await ctx.send("{}'s avatar url is: {}".format(user.mention, avatar_url))

    @commands.command()
    async def defaultavatar(self, ctx, *, user:discord.User=None):
        """Gets your default avatar url or the default avatar url of the specified user"""
        if user is None:
            user = ctx.message.author
        await ctx.send("{}'s default avatar url is: {}".format(user.mention, user.default_avatar_url))
    #/s
    @commands.command()
    async def emoteurl(self, ctx, *, emote:str):
        """Gets the url for a CUSTOM emote (meaning no unicode emotes)"""
        emote_id = None
        try:
            if extract_emote_id(emote) is not None:
                emote_id = extract_emote_id(emote)
        except:
            pass
        if emote_id is None:
            await ctx.send("That is not a custom emote")
            return
        await ctx.send("https://discordapp.com/api/emojis/{}.png".format(emote_id))

    @commands.command()
    async def discr(self, ctx, *, discriminator:str):
        """Gets a username#discriminator list of all users that the bot can see with the specified discriminator"""
        members = []
        for member in list(self.bot.get_all_members()):
            if member.discriminator == discriminator and str(member) not in members:
                members.append(str(member))
        if len(members) == 0:
            members = "Well, I don't see anyone with `{}` anywhere really...".format(discriminator)
        else:
            members = "```{}```".format(", ".join(members))
        await ctx.send(members)

    @commands.command()
    async def daystillhalloween(self, ctx):
        """Displays how many days until it's halloween"""
        await ctx.send("Days until halloween: `{} days`".format((halloween - datetime.today()).days))

    @commands.command()
    async def daystillchristmas(self, ctx):
        """Displays how many days until it's christmas"""
        await ctx.send("Days until christmas: `{} days`".format((christmas - datetime.today()).days))

    @commands.command()
    async def daystillnewyears(self, ctx):
        """Displays how many days until it's the new year"""
        await ctx.send("Days until new years: `{} days`".format((newyear - datetime.today()).days))

    @commands.command()
    async def getserverinfo(self, ctx, *, name:str):
        """Gets very basic server info on the server with the specified name"""
        guild = discord.utils.get(self.bot.guilds, name=name)
        if guild is None:
            await ctx.send("I could not find a server by the name of `{}`".format(name))
        else:
            await ctx.send("```Name: {}\nID: {}\nOwner: {}\nOwner ID: {}\nMember count: {}\nDate created: {}```".format(guild.name, guild.id, guild.owner, guild.owner.id, len(guild.members), format_time(guild.created_at)))

    @commands.command()
    async def isitdown(self, ctx, *, url:str):
        """Checks to see if a website is online or not"""
        await ctx.channel.trigger_typing()
        url = url.strip("<>")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://{}".format(url)
        try:
            starttime = time.time()
            requests.get(url, timeout=3)
            ping = "%.01f seconds" % (time.time() - starttime)
            await ctx.send("`{}` is online. Ping time is `{}`".format(url, ping))
        except Exception as e:
            await ctx.send("`{}` is offline.".format(url))
            await ctx.send("Error {}".format(e))

    @commands.command()
    async def getemotes(self, ctx):
        """Gets a list of the server's emotes"""
        emotes = ctx.guild.emojis
        if len(emotes) == 0:
            await ctx.send("This server does not have any emotes!")
            return
        emotes = ["`:{}:` = {}".format(emote.name, emote) for emote in emotes]
        await ctx.send("Current emotes for this server\n" + "\n".join(emotes))

    @commands.command()
    async def osu(self, ctx, *, username:str):
        """Gets an osu! profile stats with the specified name"""
        if not config.enableOsu:
            await ctx.send("The osu! command has been disabled.")
            return
        try:
            import osuapi
        except ImportError:
            log.critical("The osu api is enabled, but the osuapi module was not found! Please run \"pip install osuapi\"")
            await ctx.send("Couldn't import the osu! api module, contact the bot developer!")
            return
        await ctx.channel.trigger_typing()
        api = osuapi.OsuApi(config.osuKey, connector=osuapi.AHConnector())
        try:
            user = await api.get_user(username)
        except osuapi.HTTPError as e:
            if e.code == 401:
                log.critical("An invalid osu! api key was set, please check the config for instructions on how to get a proper api key!")
                await ctx.send("An invalid osu! api key was set, contact the bot developer!")
            else:
                log.critical("An unknown error occured while trying to get an osu! profile.")
                await ctx.send("An unknown error occured while trying to get that user's osu! profile, contact the bot developer!")
        try:
            user = user[0]
        except IndexError:
            await ctx.send("Could find any osu! profile named `{}`".format(username))
            return
        fields = {"ID":user.user_id, "Country":user.country, "Level":int(user.level), "Hits":user.total_hits, "Score":user.total_score, "Accuracy":"{0:.2f}%".format(user.accuracy), "Play Count":user.playcount, "Ranked Score":user.ranked_score, "A rank":user.count_rank_a, "S rank":user.count_rank_s, "SS rank":user.count_rank_ss}
        embed = make_list_embed(fields)
        embed.title = "{}'s osu! Stats".format(user.username)
        embed.color = 0xFF00FF
        embed.set_thumbnail(url="http://s.ppy.sh/a/{}".format(user.user_id))
        await ctx.send(embed=embed)

    @commands.command()
    async def donate(self, ctx):
        """give me money"""
        await ctx.send("Have money? Want to give it to me? https://donate.dragonfire.me/")

    @commands.command()
    async def st(self, ctx):
        """Speedtest.net results"""
        rb = "```rb\n{0}\n```"
        await ctx.channel.trigger_typing()
        msg = "speedtest-cli --share --simple"
        input = os.popen(msg)
        output = input.read()
        await ctx.send(rb.format(output))
        # msg.replace("serverip", "Server IP").replace("\n", "\n").replace("\"", "").replace("b'", "").replace("'",
        #                                                                                                     "")))

    @commands.command()
    async def emoteinfo(self, ctx, *, emote:discord.Emoji):
        """Gets information on a custom emote (Only works for servers the bot is on)"""
        fields = {"Name":emote.name, "ID":emote.id, "Server Origin":emote.guild.name, "Created On":format_time(emote.created_at), "Colons Required":emote.require_colons, "Managed by Twitch":emote.managed}
        embed = make_list_embed(fields)
        embed.title = ":{}:".format(emote.name)
        embed.color = 0xFF0000
        embed.set_thumbnail(url=emote.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def ipping(self, ctx, *, ip: str):
        """Pings to an ip address or domain"""
        rb = "```rb\n{0}\n```"
        await ctx.channel.trigger_typing()
        msg = "ping -c 4 {0}".format(ip)
        input = os.popen(msg)
        output = input.read()
        await ctx.send(rb.format(output))

    @commands.command()
    async def traceroute(self, ctx, *, ip: str):
        """Traces the route to the connection of a website or IP"""
        rb = "```rb\n{0}\n```"
        await ctx.channel.trigger_typing()
        msg = "traceroute {0}".format(ip)
        input = os.popen(msg)
        output = input.read()
        await ctx.send(rb.format(output))

    @commands.command()
    async def getnumericip(self, ctx, address:str):
        """Resolves the numeric ip of a domain"""
        try:
            await ctx.send(socket.gethostbyname(address))
        except socket.gaierror:
            await ctx.send("`{}` is not a valid address".format(address))

    @commands.command()
    async def getuserbyid(self, ctx, id:int):
        """Gets a user by id"""
        user = discord.utils.get(list(self.bot.get_all_members()), id=id)
        if not user:
            await ctx.send("Could not find any user in my mutual servers with an ID of `{}`".format(id))
            return
        if user.activity:
            game = user.activity.name
        else:
            game = None
        fields = {"Name":user.name, "Discriminator":user.discriminator, "ID":user.id, "Status":str(user.status).replace("dnd", "do not disturb"), "Game":game, "Bot":user.bot}
        embed = make_list_embed(fields)
        embed.title = str(user)
        embed.color = 0xFF0000
        embed.set_thumbnail(url=get_avatar(user))
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def roleid(self, ctx, role:discord.Role):
        """Gets the id for the specified role"""
        await ctx.send("The role ID for `{}` is `{}`".format(role.name, role.id))

def setup(bot):
    bot.add_cog(Information(bot))