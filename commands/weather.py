import os
#import forecastiopy
import geocoder
import json
import discord

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
        if ctx.message.author == ctx.message.author: #filler
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
                if current.precipProbability == 0:
                	var = "It's not raining, is it?"
                else:
                	var = "Looks like it's raining."
                if ctx.message.server.me.color == None:
                	maybe = None
                else:
                	maybe = ctx.message.server.me.color
                em.set_thumbnail(url="https://dragonfire.me/474be77b-23bc-42e4-a779-6eb7b3b9a892.jpg")
                em.color = maybe
                em.add_field(name='Temperature', value="{}°F".format(current.temperature), inline=True)
                em.add_field(name='Precipitation', value=var, inline=True)
                em.add_field(name='Humidity', value="{:.0%}".format(current.humidity), inline=True)
                await self.bot.say(embed=em)
            except Exception as fucking_hell:
                await self.bot.say("```py\n{}\n```".format(fucking_hell))
        else:
            await self.bot.say("Location isn't found or the given zip code or address is too short. Try again.")

    @commands.command(pass_context=True)
    async def locate(self, ctx, *, address: str):
        try:
            g = geocoder.google(address)
            loc = g.json
            var = json.dumps(loc)
            k = json.loads(var)
            if k['status'] == 'OK':
            	yes = k['address']
            elif k['status'] == 'ZERO_RESULTS':
            	yes = "There's no results found for this location."
            await self.bot.say(yes)
        except Exception as e:
            await self.bot.say("```py\n{}\n```".format(e))

def setup(bot):
    bot.add_cog(Weather(bot))