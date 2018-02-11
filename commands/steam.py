from __future__ import print_function

import asyncio
import datetime

from steam import WebAPI
from utils.tools import *

from discord.ext import commands
from utils.logger import log
from utils.sharding import steamapikey

try:
    api = WebAPI(key=steamapikey)
    log.info("Logged in to Steam via API Key")
except Exception as e:
    log.error("Error!\n" + e)

class Steam():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def steamprofile(self, ctx, vanityurl: str):
        try:
            sid = api.ISteamUser.ResolveVanityURL(vanityurl=vanityurl)['response']['steamid']
            username = api.ISteamUser.GetPlayerSummaries_v2(steamids=sid)['response']['players'][0]['personaname']
            steamid = api.ISteamUser.GetPlayerSummaries_v2(steamids=sid)['response']['players'][0]['steamid']
            creationdaten = api.ISteamUser.GetPlayerSummaries_v2(steamids=sid)['response']['players'][0]['timecreated']
            lastlogoutn = api.ISteamUser.GetPlayerSummaries_v2(steamids=sid)['response']['players'][0]['lastlogoff']
            creationdate = datetime.fromtimestamp(int(creationdaten)).strftime('%A %B %d, %Y at %I:%M %p')
            lastlogout =  datetime.fromtimestamp(int(lastlogoutn)).strftime('%A %B %d, %Y at %I:%M %p')
            avatarthing = api.ISteamUser.GetPlayerSummaries_v2(steamids=sid)['response']['players'][0]['avatarfull']
            profilestatus = api.ISteamUser.GetPlayerSummaries_v2(steamids=sid)['response']['players'][0]['profilestate']
            if profilestatus is 1:
                status = "Offline"
            elif profilestatus is 0:
                status = "Online"

            em = discord.Embed(description="")
            if ctx.me.color == None:
                maybe = None
            else:
                maybe = ctx.me.color
            em.color = maybe
            em.title = "Steam Profile Info"
            em.set_thumbnail(url=avatarthing)
            em.add_field(name='Username', value=username)
            em.add_field(name='Status', value=status)
            em.add_field(name='Vanity URL', value=vanityurl)
            em.add_field(name='Steam ID', value=steamid)
            em.add_field(name='Date Created', value=creationdate)
            em.add_field(name='Last logged out', value=lastlogout)

            await ctx.send(embed=em)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    async def steamdebug(self, ctx, *, shit: str):
        try:
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            await ctx.send(py.format(rebug))
        except Exception as damnit:
            await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))



def setup(bot):
    bot.add_cog(Steam(bot))