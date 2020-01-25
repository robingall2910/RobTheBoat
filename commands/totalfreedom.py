import discord

from utils import checks
from discord.ext import commands

class TotalFreedom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['tftest'])
    async def tf(self, ctx):
        """aaa"""
        await ctx.send("it still works")

def setup(bot):
    bot.add_cog(TotalFreedom(bot))