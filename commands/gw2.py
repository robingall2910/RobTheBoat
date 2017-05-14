import requests
import json #blobthinkingbutfast
import os

from guildwars2api.client import GuildWars2API
from discord.ext import commands

class GW2():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    async def gw2test(self, ctx):
        api = GuildWars2API(api_version='v2') #default main ver
        """A test for the Guild Wars 2 extension."""
        matches = api.matches.get()
        await bot.say("Matches: {}".format(len(matches)))

    @commands.command(pass_context=True, hidden=True)
    async def itemlookup(self, ctx, item: int):
        api = GuildWars2API(api_version='v2') # v1 only
        """Looks up an item from Guild Wars 2, item ID only / Don't know the ID? Look it up here: https://wiki.guildwars2.com/wiki/Main_Page"""
        task = api.item_details.get(item)
        meme = task.json
        await bot.say("Name: {}\nItem ID:{}\nDesc: {}\nType: {}".format(meme['name'], meme['item_id'], meme['description'], meme['type']))

#idk

def setup(bot):
    bot.add_cog(GW2(bot))