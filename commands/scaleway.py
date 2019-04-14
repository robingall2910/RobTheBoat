import discord
import asyncio

from discord.ext import commands
from scaleway.apis import ComputeAPI
from utils import checks
from utils.tools import py
from utils.config import Config

config = Config()
api = ComputeAPI(auth_token=config._scalewayKey, region='ams1')

class Scaleway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_dev()
    async def debugscaleway(self, ctx, *, shit: str):
        """This is the part where I make 20,000 typos before I get it right"""
        # "what the fuck is with your variable naming" - EJH2
        # seth seriously what the fuck - Robin
        try:
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            await ctx.send(py.format(rebug))
        except Exception as damnit:
            rebug = eval(shit)
            print(rebug)
            await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))

    @commands.command()
    async def scalewayinfo(self, ctx):
        try:
            a = api.query().servers('45583a4e-1059-4395-949a-00ed763e334c').get()
        except Exception as e:
            print(e)
            return
        em = discord.Embed(description=a['server']['name'])
        em.title("Scaleway Server Info")
        em.add_field(name="Status", value=a['server']['state_detail'])
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Scaleway(bot))