import os
#import forecastiopy
import geocoder
import json

from forecastiopy import *
from pprint import pprint
from discord.ext import commands
from utils.sharding import darkskyapi

api_key = darkskyapi

class Weather():
    def __init__(self, bot):
        self.bot = bot
############TROY DID NOT CONTRIBUTE HERE AT ALL
    """@commands.command(pass_context=True)
    async def weather(self, ctx, *, address: str):
        if ctx.message.server.id == ctx.message.server.id: #IF THIS DOESNT FUCKING WORK
            try:
                g = geocoder.google(address)
                results = g.latlng
                fio = ForecastIO.ForecastIO(api_key, latitude=results[0], longitude=results[1],
                                            units=ForecastIO.ForecastIO.UNITS_US)
                current = FIOCurrently.FIOCurrently(fio)
                if fio.has_flags() is True:
                	flags = FIOFlags.FIOFlags(fio)
                	pprint(vars(flags))
                loc = geocoder.google(address)
                k = loc.json
                if flags:
                	await self.bot.say(str(ctx.message.author) + " >> Currently in {}: `{} F` with a humidity percentage of `{:.0%}`. Chance of rain: `{:.0%}`. Alerts: {}".format(k['city'] + ", " + k['state'], current.temperature, current.humidity, current.precipProbability, flags.units))
                else:
                	await self.bot.say(str(ctx.message.author) + " >> Currently in {}: `{} F` with a humidity percentage of `{:.0%}`. Chance of rain: `{:.0%}`. Alerts: None.".format(k['city'] + ", " + k['state'], current.temperature, current.humidity, current.precipProbability))
            except Exception as e:
                await self.bot.say("```py\n{}\n```".format(e))
        else:
            await self.bot.say("Location isn't found or the given zip code or address is too short. Try again.")"""

    @commands.command(pass_context=True)
    async def weather(self, ctx, *, address: str):
        if False is True == False: #filler
        #fine thanks troy
            try:
                g = geocoder.google(address)
                results = g.latlng
                fio = ForecastIO.ForecastIO(api_key, latitude=results[0], longitude=results[1],
                                            units=ForecastIO.ForecastIO.UNITS_US)
                current = FIOCurrently.FIOCurrently(fio)
                loc = geocoder.google(address)
                k = loc.json
                #you forgot literally all of the location resolving
                em = discord.Embed(description="\u200b")
                em.title = "{}, {}'s Weather".format(k['city'], k['state'])
                #you did this wrong though
                em.set_thumbnail(url="https://canary.discordapp.com/assets/ccf4c733929efd9762ab02cd65175377.svg")
                em.add_field(name='Temperature', value=current.temperature, inline=True)
                em.add_field(name='Precipitation', value=current.precipProbability, inline=True)
                em.add_field(name='Humidity', value=current.humidity, inline=True)
                await bot.say(embed=em)
        else:
                await self.bot.say("Location isn't found or the given zip code or address is too short. Try again.")

    @commands.command(pass_context=True)
    async def locate(self, ctx, *, address: str):
        try:
            g = geocoder.google(address)
            loc = g.json
            var = json.dumps(loc)
            k = json.loads(var)
            await self.bot.say(k['address'])
        except Exception as e:
            await self.bot.say("```py\n{}\n```".format(e))

def setup(bot):
    bot.add_cog(Weather(bot))