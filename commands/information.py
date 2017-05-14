import os

from discord.ext import commands
from datetime import *
from utils.tools import *
from utils.logger import log
from utils.config import Config
config = Config()

halloween = date(2017, 10, 31)
christmas = date(2017, 12, 25)
newyear = date(2018, 1, 1)

class Information():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def id(self, ctx, user:discord.User=None):
        """Gets your ID or if you @mention a user it gets their id"""
        if user is None:
            await self.bot.say("Your ID is `{}`".format(ctx.message.author.id))
        else:
            await self.bot.say("{}'s ID is `{}`".format(user.mention, user.id))

    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        """Gets information on the current server"""
        server = ctx.message.server
        if not server.afk_channel:
            afk_channel = "None"
        else:
            afk_channel = server.afk_channel.name
        await self.bot.say(xl.format("~~~~~~~~~Server Info~~~~~~~~\nName: {}\nID: {}\nIcon URL: {}\nTotal Members: {}\nCreated: {}\nRegion: {}\nOwner: {}\nOwner ID: {}\nAFK Channel: {}\nAFK timeout: {}\nRoles: {}\nChannels: {}").format(server.name, server.id, server.icon_url, server.member_count, server.created_at, server.region, server.owner, server.owner_id, afk_channel, server.afk_timeout, len(server.roles), len(server.channels)))

    @commands.command(pass_context=True)
    async def userinfo(self, ctx, *, user:discord.Member=None):
        """Gets your information or the information of the specified user"""
        if user is None:
            user = ctx.message.author
        roles = ", ".join(map(str, user.roles))
        if roles == "@everyone":
            roles = None
        else:
            roles = roles.strip("@everyone, ")
        if not user.avatar_url:
            avatar_url = user.default_avatar_url
        else:
            avatar_url = user.avatar_url
        await self.bot.say(xl.format("~~~~~~~~~{}~~~~~~~~\nUsername: {}\nDiscriminator: {}\nID: {}\nBot: {}\nAvatar URL: {}\nAccount created: {}\nGame: {}\nStatus: {}\nVoice channel: {}\nServer muted: {}\nServer deafened: {}\nRoles: {}").format(user, user.name, user.discriminator, user.id, user.bot, avatar_url, user.created_at, str(user.game), str(user.status), str(user.voice_channel), user.mute, user.deaf, roles))

    @commands.command(pass_context=True)
    async def avatar(self, ctx, *, user:discord.User=None):
        """Gets your avatar url or the avatar url of the specified user"""
        if user is None:
            user = ctx.message.author
        if not user.avatar_url:
            avatar_url = user.default_avatar_url
        else:
            avatar_url = user.avatar_url
        await self.bot.say("{}'s avatar url is: {}".format(user.mention, avatar_url))

    @commands.command(pass_context=True)
    async def defaultavatar(self, ctx, *, user:discord.User=None):
        """Gets your default avatar url or the default avatar url of the specified user"""
        if user is None:
            user = ctx.message.author
        await self.bot.say("{}'s default avatar url is: {}".format(user.mention, user.default_avatar_url))

    @commands.command(pass_context=True)
    async def roleinfo(self, ctx, *, name:str):
        """Gets information on a role, warning, it might take up the entire screen"""
        role = discord.utils.get(ctx.message.server.roles, name=name)
        if role is None:
            await self.bot.say("`{}` isn't real. Or is it?".format(name))
            return
        color = role.color
        if color == discord.Color(value=0x000000):
            color = "None"
        count = len([member for member in ctx.message.server.members if discord.utils.get(member.roles, name=role.name)])
        perms = role.permissions
        permlist = "Can ban members: {}\nCan change nickname: {}\nCan connect to voice channels: {}\nCan create instant invites: {}\nCan deafen members: {}\nCan embed links: {}\nCan use external emojis: {}\nCan manage channel: {}\nCan manage emojis: {}\nCan manage messages: {}\nCan manage nicknames: {}\nCan manage roles: {}\nCan manage server: {}\nCan mention everyone: {}\nCan move members: {}\nCan mute members: {}\nCan read message history: {}\nCan send messages: {}\nCan speak: {}\nCan use voice activity: {}\nCan manage webbooks: {}\nCan add reactions: {}".format(perms.ban_members, perms.change_nickname, perms.connect, perms.create_instant_invite, perms.deafen_members, perms.embed_links, perms.external_emojis, perms.manage_channels, perms.manage_emojis, perms.manage_messages, perms.manage_nicknames, perms.manage_roles, perms.manage_server, perms.mention_everyone, perms.move_members, perms.mute_members, perms.read_message_history, perms.send_messages, perms.speak,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               perms.use_voice_activation, perms.manage_webhooks, perms.add_reactions)
        await self.bot.say(py.format("Name: \"{}\"\nID: {}\nColor: {}\nPosition: {}\nUser count: {}\nMentionable: {}\nDisplay separately: {}\n".format(role.name, role.id, color, role.position, count, role.mentionable, role.hoist) + permlist))

    @commands.command()
    async def emoteurl(self, *, emote:discord.Emoji):
        """Gets the url for a CUSTOM emote (meaning no emotes like :eyes: and :ok_hand: sorry)"""
        await self.bot.say(emote.url)

    @commands.command()
    async def discr(self, *, discriminator:str):
        """Gets a username#discriminator list of all users that the bot can see with the specified discriminator"""
        members = []
        for member in list(self.bot.get_all_members()):
            if member.discriminator == discriminator and str(member) not in members:
                members.append(str(member))
        if len(members) == 0:
            members = "Well, I don't see anyone with `{}` anywhere really...".format(discriminator)
        else:
            members = "```{}```".format(", ".join(members))
        await self.bot.say(members)

    @commands.command()
    async def daystillhalloween(self):
        """Displays how many days until it's halloween"""
        await self.bot.say("Days until halloween: `{} days`".format((halloween - date.today()).days))

    @commands.command()
    async def daystillchristmas(self):
        """Displays how many days until it's christmas"""
        await self.bot.say("Days until christmas: `{} days`".format((christmas - date.today()).days))

    @commands.command()
    async def daystillnewyears(self):
        """Displays how many days until it's christmas"""
        await self.bot.say("Days until new years: `{} days`".format((newyear - date.today()).days))

    @commands.command()
    async def getserverinfo(self, *, name:str):
        """Gets very basic server info on the server with the specified name"""
        server = discord.utils.get(self.bot.servers, name=name)
        if server is None:
            await self.bot.say("I don't know `{}` is. Is that some kind of server I don't know of?!?".format(name))
        else:
            await self.bot.say("```Name: {}\nID: {}\nOwner: {}\nOwner ID: {}\nMember count: {}\nDate created: {}```".format(server.name, server.id, server.owner, server.owner.id, len(server.members), server.created_at))

    @commands.command(pass_context=True)
    async def isitdown(self, ctx, *, url:str):
        """Checks to see if a website is online or not"""
        await self.bot.send_typing(ctx.message.channel)
        url = url.strip("<>")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://{}".format(url)
        try:
            starttime = time.time()
            r = requests.get(url, timeout=3)
            ping = "%.01f seconds" % (time.time() - starttime)
            await self.bot.say("`{}` is online. Ping time is `{}`".format(url, ping))
        except:
            await self.bot.say("`{}` is offline.".format(url))

    @commands.command(pass_context=True)
    async def getemotes(self, ctx):
        """Gets a list of the server's emotes"""
        emotes = ctx.message.server.emojis
        if len(emotes) == 0:
            await self.bot.say("This server does not have any emotes!")
            return
        emotes = ["`:{}:` = {}".format(emote.name, emote) for emote in emotes]
        await self.bot.say("Current emotes for this server\n" + "\n".join(emotes))

    @commands.command(pass_context=True)
    async def osu(self, ctx, *, username:str):
        """Gets an osu! profile stats with the specified name"""
        if not config.enableOsu:
            await self.bot.say("The osu command is currently disabled.")
            return
        try:
            import osuapi
        except ImportError:
            log.critical("The osu api is enabled, but the osuapi module was not found! Please run \"pip install osuapi\"")
            await self.bot.say("Couldn't import the osu! api module, contact the bot developer!")
            return
        await self.bot.send_typing(ctx.message.channel)
        api = osuapi.OsuApi(config._osuKey, connector=osuapi.AHConnector())
        try:
            user = await api.get_user(username)
        except osuapi.HTTPError as e:
            if e.code == 401:
                log.critical("An invalid osu! api key was set, please check the config for instructions on how to get a proper api key!")
                await self.bot.say("An invalid osu! api key was set, contact the bot developer!")
                return
            else:
                log.critical("An unknown error occured while trying to get an osu! profile.")
                await self.bot.say("An unknown error occured while trying to get that user's osu! profile, contact the bot developer!")
                return
        try:
            user = user[0]
        except IndexError:
            await self.bot.say("Could find any osu! profile named `{}`".format(username))
            return
        results = discord.Embed(description="\u200b")
        results.title = user.username + "'s osu! stats"
        results.add_field(name='ID', value=user.user_id)
        results.add_field(name='Country', value=user.country)
        results.add_field(name='Level', value=int(user.level))
        results.add_field(name='Total Hits', value=user.total_hits)
        results.add_field(name='Total Score', value=user.total_score)
        results.add_field(name='Accuracy', value="{0:.2f}%".format(user.accuracy))
        results.add_field(name='Play Count', value=user.playcount)
        results.add_field(name='Ranked Score', value=user.ranked_score)
        results.add_field(name='A Rank Count/S Rank Count/SS Rank Count', value="{}/{}/{}".format(user.ranked_score,user.count_rank_a, user.count_rank_s, user.count_rank_ss))
        await self.bot.say(embed=results)
        
    @commands.command(pass_context=True)
    async def donate(self, ctx):
        await self.bot.say("https://donate.dragonfire.me/ pls give me money xdxd (Wells Fargo SurePay also exists, but that's when you really can't donate via PayPal)")

    @commands.command(pass_context=True)
    async def st(self, ctx):
        rb = "```rb\n{0}\n```"
        await self.bot.send_typing(ctx.message.channel)
        msg = "speedtest-cli --share --simple"
        input = os.popen(msg)
        output = input.read()
        await self.bot.send_message(ctx.message.channel, rb.format(output))
        # msg.replace("serverip", "Server IP").replace("\n", "\n").replace("\"", "").replace("b'", "").replace("'",
        #                                                                                                     "")))
    
    @commands.command(pass_context=True)
    async def ipping(self, ctx, *, ip: str):
        rb = "```rb\n{0}\n```"
        await self.bot.send_typing(ctx.message.channel)
        msg = "ping -c 4 {0}".format(ip)
        input = os.popen(msg)
        output = input.read()
        await self.bot.send_message(ctx.message.channel, rb.format(output))

    @commands.command(pass_context=True)
    async def traceroute(self, ctx, *, ip: str):
        rb = "```rb\n{0}\n```"
        await self.bot.send_typing(ctx.message.channel)
        msg = "traceroute {0}".format(ip)
        input = os.popen(msg)
        output = input.read()
        await self.bot.send_message(ctx.message.channel, rb.format(output))

def setup(bot):
    bot.add_cog(Information(bot))
