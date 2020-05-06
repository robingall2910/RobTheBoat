import discord
import hypixel

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
        ctx.send(f"The player {username} is {player.getRank()}. That's all I have to say.")

def setup(bot):
    bot.add_cog(Hypixel(bot))



