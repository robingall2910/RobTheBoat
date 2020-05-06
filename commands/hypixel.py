import discord
import hypixel
import asyncio

from discord.ext import commands
from utils.config import Config
from utils.logger import log
from utils import checks
from utils.tools import *

config = Config()

key = [config._hypixelKey]
hypixel.setKeys(key)

class Hypixel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hypixeltest(self, ctx, username: str):
        player = hypixel.Player(username)
        await ctx.send(f"The player {username} is {player.getRank()['rank']}. That's all I have to say.")


    @commands.command()
    @checks.is_dev()
    async def hdebug(self, ctx, *, shit: str):
        try:
            player = hypixel.Player("usefulnt")
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            else:
                await ctx.send(py.format(rebug))
        except Exception as damnit:
            await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))
def setup(bot):
    bot.add_cog(Hypixel(bot))



