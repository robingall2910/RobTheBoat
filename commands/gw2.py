import asyncio
import json

from discord.ext import commands
from utils.config import Config
from utils.logger import log
from utils import checks
from utils.tools import *
from gw2api import GuildWars2Client

config = Config()

gw2 = GuildWars2Client(api_key=config._gw2Key)

log.info("Getting Guild Wars 2 info...")
log.info(gw2)

class GuildWars2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gwtest(self, ctx):
        g = json.dumps(gw2.build.get()['id'])
        await ctx.send(g)

    @commands.command()
    @checks.is_dev()
    async def guildsearch(self, ctx, *, gname: str):
        g = json.dumps(gw2.guildsearch.get(name=gname)[0])
        r = g.replace('"', '')
        try:
            h = json.dumps(gw2.guildidmembers.get(r))
        except Exception as e:
            ctx.send(e)
        if "no such guild" in h:
            h = "nothin"
        em = discord.Embed(description="\n")
        if h == "nothin":
            em.color = 0x0098eb
            em.add_field(name='Info', value='No such guild has been found! Type it in exactly as is.')
        else:
            em.color = ctx.me.color
            em.add_field(name='Members', value=h)
        em.title("Guild Info")
        await ctx.send(embed=em)

    @commands.command()
    @checks.is_dev()
    async def gwdebug(self, ctx, *, shit: str):
        try:
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            if len(rebug) >= 2000:
                await ctx.send(py.format(rebug[:1984]))
                await ctx.send(py.format(rebug[1984:]))
            else:
                await ctx.send(py.format(rebug))
        except Exception as damnit:
            await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))


def setup(bot):
    bot.add_cog(GuildWars2(bot))