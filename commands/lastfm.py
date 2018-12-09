import asyncio
import json
import urllib

import pylast

from discord.ext import commands
from utils.config import Config
from utils import checks
from utils.tools import *
from utils.logger import log

config = Config()

api = config._lastfmapiKey
secret = config._lastfmSecret

try:
    network = pylast.LastFMNetwork(api_key=api, api_secret=secret)
    log.info("Connected to the Last.fm Network!")
except Exception as e:
    log.error("Error!\n" + e)

class Lastfm():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def songinfo(self, ctx, *, song: str):
        url = "http://ws.audioscrobbler.com/2.0/?method=track.search&track={}&api_key={}&format=json".format(song, api)
        req = urllib.request.Request(url, data=None)
        response = urllib.request.urlopen(req)
        resp = json.loads(response.read().decode('utf-8'))
        title = resp['results']['trackmatches']['track'][0]['name']
        artist = resp['results']['trackmatches']['track'][0]['artist']
        url2 = "http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={}&artist={}&track={}&format=json".format(api, artist, title)
        req2 = urllib.request.Request(url2, data=None)
        response2 = urllib.request.urlopen(req2)
        resp2 = json.loads(response2.read().decode('utf-8'))
        em = discord.Embed(description="Last.fm metadata")
        try:
            em.color = ctx.me.color
        except:
            pass
        em.title = resp2['track']['artist']['name'] + " - " + resp2['track']['name']
        try:
            em.add_field(name="Album name", value=resp2['track']['album']['title'])
        except:
            pass
        try:
            em.add_field(name="Last.fm URL", value=resp2['track']['url'])
        except:
            pass
        try:
            em.add_field(name="Song duration", value=resp2['track']['duration'])
        except:
            pass
        try:
            em.add_field(name="Listeners", value=resp2['track']['listeners'])
        except:
            pass
        try:
            em.add_field(name="Play count", value=resp2['track']['playcount'])
        except:
            pass
        try:
            em.set_thumbnail(url=resp2['track']['album']['image'][3]['#text'])
        except:
            pass
        try:
            tags = str(resp2['track']['toptags']['tag'][0]['name']) + ", " + str(resp2['track']['toptags']['tag'][1]['name']) + ", " + str(resp2['track']['toptags']['tag'][2]['name']) + ", " + str(resp2['track']['toptags']['tag'][3]['name']) + ", " + str(resp2['track']['toptags']['tag'][4]['name'])
        except:
            tags = None
        em.add_field(name="Top tags", value=tags)
        await ctx.send(embed=em)

    @commands.command()
    async def fmuserrecent(self, ctx, *, user: str):
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={}&api_key={}&format=json&limit=12".format(user, api)
        req = urllib.request.Request(url, data=None)
        response = urllib.request.urlopen(req)
        resp = json.loads(response.read().decode('utf-8'))
        em = discord.Embed(description=None)
        user = resp['recenttracks']['@attr']['user']
        em.title = "{}'s Recent Tracks".format(user)
        try:
            em.color = ctx.me.color
        except:
            pass
        em.add_field(name=resp['recenttracks']['track'][0]['artist']['#text'],
                     value=resp['recenttracks']['track'][0]['name'])
        em.add_field(name=resp['recenttracks']['track'][1]['artist']['#text'],
                     value=resp['recenttracks']['track'][1]['name'])
        em.add_field(name=resp['recenttracks']['track'][2]['artist']['#text'],
                     value=resp['recenttracks']['track'][2]['name'])
        em.add_field(name=resp['recenttracks']['track'][3]['artist']['#text'],
                     value=resp['recenttracks']['track'][3]['name'])
        em.add_field(name=resp['recenttracks']['track'][4]['artist']['#text'],
                     value=resp['recenttracks']['track'][4]['name'])
        em.add_field(name=resp['recenttracks']['track'][5]['artist']['#text'],
                     value=resp['recenttracks']['track'][5]['name'])
        em.add_field(name=resp['recenttracks']['track'][6]['artist']['#text'],
                     value=resp['recenttracks']['track'][6]['name'])
        em.add_field(name=resp['recenttracks']['track'][7]['artist']['#text'],
                     value=resp['recenttracks']['track'][7]['name'])
        em.add_field(name=resp['recenttracks']['track'][8]['artist']['#text'],
                     value=resp['recenttracks']['track'][8]['name'])
        em.add_field(name=resp['recenttracks']['track'][9]['artist']['#text'],
                     value=resp['recenttracks']['track'][9]['name'])
        em.add_field(name=resp['recenttracks']['track'][10]['artist']['#text'],
                     value=resp['recenttracks']['track'][10]['name'])
        em.add_field(name=resp['recenttracks']['track'][11]['artist']['#text'],
                     value=resp['recenttracks']['track'][11]['name'])
        await ctx.send(embed=em)

    @commands.command()
    async def topartists(self, ctx, *, country: str):
        url = "http://ws.audioscrobbler.com/2.0/?method=geo.gettopartists&country={}&api_key={}&format=json&limit=12".format(country, api)
        req = urllib.request.Request(url, data=None)
        response = urllib.request.urlopen(req)
        resp = json.loads(response.read().decode('utf-8'))
        em = discord.Embed(description=None)
        try:
            em.color = ctx.me.color
        except:
            pass
        em.title = "Top artists for {}".format(str(resp['topartists']['@attr']['country']))
        em.add_field(name="1st",
                     value=resp['topartists']['artist'][0]['name'])
        em.add_field(name="2nd",
                     value=resp['topartists']['artist'][1]['name'])
        em.add_field(name="3rd",
                     value=resp['topartists']['artist'][2]['name'])
        em.add_field(name="4th",
                     value=resp['topartists']['artist'][3]['name'])
        em.add_field(name="5th",
                     value=resp['topartists']['artist'][4]['name'])
        em.add_field(name="6th",
                     value=resp['topartists']['artist'][5]['name'])
        em.add_field(name="7th",
                     value=resp['topartists']['artist'][6]['name'])
        em.add_field(name="8th",
                     value=resp['topartists']['artist'][7]['name'])
        em.add_field(name="9th",
                     value=resp['topartists']['artist'][8]['name'])
        em.add_field(name="10th",
                     value=resp['topartists']['artist'][9]['name'])
        em.add_field(name="11th",
                     value=resp['topartists']['artist'][10]['name'])
        em.add_field(name="12th",
                     value=resp['topartists']['artist'][11]['name'])
        await ctx.send(embed=em)

    @commands.command()
    async def toptracks(self, ctx, country: str, **kwargs):
        try:
            for locationname in kwargs.items():
                location = locationname
        except:
            location = None
        country2 = country.replace("_", " ")
        try:
            url = "http://ws.audioscrobbler.com/2.0/?method=geo.gettoptracks&country={}&location={}&api_key={}&format=json&limit=12".format(country2, location, api)
        except UnboundLocalError:
            url = "http://ws.audioscrobbler.com/2.0/?method=geo.gettoptracks&country={}&api_key={}&format=json&limit=12".format(country2, api)
        req = urllib.request.Request(url, data=None)
        response = urllib.request.urlopen(req)
        resp = json.loads(response.read().decode('utf-8'))
        em = discord.Embed(description="Tracks are by order of popularity.")
        em.title = "Top artists for {}".format(str(resp['tracks']['@attr']['country']))
        try:
            em.color = ctx.me.color
        except:
            pass
        em.add_field(name=resp['tracks']['track'][0]['name'],
                     value="by {}".format(resp['tracks']['track'][0]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][1]['name'],
                     value="by {}".format(resp['tracks']['track'][1]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][2]['name'],
                     value="by {}".format(resp['tracks']['track'][2]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][3]['name'],
                     value="by {}".format(resp['tracks']['track'][3]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][4]['name'],
                     value="by {}".format(resp['tracks']['track'][4]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][5]['name'],
                     value="by {}".format(resp['tracks']['track'][5]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][6]['name'],
                     value="by {}".format(resp['tracks']['track'][6]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][7]['name'],
                     value="by {}".format(resp['tracks']['track'][7]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][8]['name'],
                     value="by {}".format(resp['tracks']['track'][8]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][9]['name'],
                     value="by {}".format(resp['tracks']['track'][9]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][10]['name'],
                     value="by {}".format(resp['tracks']['track'][10]['artist']['name']))
        em.add_field(name=resp['tracks']['track'][11]['name'],
                     value="by {}".format(resp['tracks']['track'][11]['artist']['name']))
        await ctx.send(embed=em)

    @commands.command()
    @checks.is_dev()
    async def fmdebug(self, ctx, *, shit: str):
        try:
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            await ctx.send(py.format(rebug))
        except Exception as damnit:
            await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))

def setup(bot):
    bot.add_cog(Lastfm(bot))