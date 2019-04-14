import discord

from utils import checks
from discord.ext import commands

class Terminal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_terminal_existent()
    @commands.command()
    async def termtest(self, ctx):
        await ctx.send('this is a test for terminal bridge thing')

def setup(bot):
    bot.add_cog(Terminal(bot))
