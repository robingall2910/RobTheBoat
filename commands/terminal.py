import discord

from utils import checks
from discord.ext import commands

class Terminal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command
    async def pensive(self, ctx):
        """pensivr"""
        await ctx.send("<@117678528220233731>")


def setup(bot):
    bot.add_cog(Terminal(bot))