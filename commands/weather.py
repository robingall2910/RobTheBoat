#import forecastiopy
import geocoder
import json
import discord
import datetime

from forecastiopy import *
from darksky import forecast
from discord.ext import commands
from utils.sharding import darkskyapi

api_key = darkskyapi

class Weather():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weather(self, ctx, *, address: str):
        """Dark Sky Weather Results"""
        if ctx.message.author == ctx.message.author: #filler
            try:
                g = geocoder.google(address)
                results = g.latlng
                loc = g.address
                #if any(sin in address for sin in the_sin):
                #    theresult = True
                #else:
                #    theresult = False
                if ", USA" in loc:
                    thedisplay = True
                    thevariable = True
                elif ", USA" not in loc:
                    thedisplay = False
                    thevariable = False
                if ", UK" in loc:
                    print("Passing as United Kingdom")
                    fio = ForecastIO.ForecastIO(api_key, latitude=results[0], longitude=results[1], units=ForecastIO.ForecastIO.UNITS_UK)
                if ", Canada" in loc:
                    print("Passing as Canada")
                    fio = ForecastIO.ForecastIO(api_key, latitude=results[0], longitude=results[1], units=ForecastIO.ForecastIO.UNITS_CA)
                else:
                    print("Passing with an automatic unit")
                    fio = ForecastIO.ForecastIO(api_key, latitude=results[0], longitude=results[1])
                current = FIOCurrently.FIOCurrently(fio)
                ds = forecast(api_key, int(results[0]), int(results[1]))
                if thedisplay == True:
                    print("The display passed")
                    em = discord.Embed(description="This information is displayed in Farenheit.")
                elif thedisplay == False:
                    print("The display didn't pass")
                    em = discord.Embed(description="This information is displayed in Celcius.")
                em.title = "{}'s Current Weather".format(loc)
                if current.uvIndex == 0:
                    uvresult = "There probably isn't any sun right now."
                    uvint = "0"
                elif current.uvIndex == range(1, 5):
                    uvresult = "Few sun rays are hitting."
                    uvint = current.uvIndex
                elif current.uvIndex == range(5, 8):
                    uvresult = "Hm.. The sun might be a bit stronk. Wear sunscreen if you're going out."
                    uvint = current.uvIndex
                elif current.uvIndex == range(8, 15):
                    uvresult = "Damn, the sun rays are hitting good here! Wear sunscreen definitely!"
                    uvint = current.uvIndex
                else:
                    uvresult = "Not available."
                    uvint = "N/A"
                try:
                    visib = current.visibility
                except AttributeError:
                    visib = "N/A"
                if ctx.me.color == None:
                    maybe = None
                else:
                    maybe = ctx.me.color
                try:
                    expiretime = datetime.datetime.fromtimestamp(int(ds.alerts[0].expires)).strftime('%A %B %d, %Y %I:%M %Z')
                    print("expire time passed")
                    counties = ', '.join(ds['alerts']['0']['regions'])
                    print("joining counties passed")
                    alertresult = "{} in {}, expiring at {}. More info [at NWS]({} 'National Weather Service')".format(ds.alerts[0].title, counties, expiretime, ds.alerts[0].uri)
                    print("alert setup complete")
                except Exception as e:
                    alertresult = e
                em.set_thumbnail(url="https://dragonfire.me/474be77b-23bc-42e4-a779-6eb7b3b9a892.jpg")
                em.color = maybe
                if thevariable == True:
                    print("The variable passed")
                    em.add_field(name='Temperature', value="{}°F".format(current.temperature), inline=True)
                elif thevariable == False:
                    print("The variable didn't pass")
                    em.add_field(name='Temperature', value="{}°C".format(current.temperature), inline=True)
                em.add_field(name='Currently', value="{}".format(current.summary), inline=True)
                em.add_field(name='Humidity', value="{:.0%}".format(current.humidity), inline=True)
                #this is a bit tricky when it comes to some countries so i'll leave it as is
                if ", UK" in loc:
                    print("speeds as UK")
                    em.add_field(name='Wind Speed/Gust (imperial)', value="{} mph/{} mph".format(current.windSpeed, current.windGust), inline=True)
                if ", USA" in loc:
                    print("speeds as America")
                    em.add_field(name='Wind Speed/Wind Gust', value="{} mph/{} mph".format(current.windSpeed, current.windGust), inline=True)
                else:
                    print("speeds in Metric (automatic)")
                    em.add_field(name='Wind Speed/Gust', value="{} km/h/{} km/h".format(current.windSpeed, current.windGust), inline=True)
                #same for this
                if ", UK" in loc:
                    print("visibilty as UK")
                    em.add_field(name='Visibility (imperial)', value="{} miles".format(visib), inline=True)
                if ", USA" in loc:
                    print("visibility as America")
                    em.add_field(name='Visibility', value="{} miles".format(visib), inline=True)
                else:
                    print("visibility in Metric (automatic)")
                    em.add_field(name='Visibility', value="{} kilometers".format(visib), inline=True)
                em.add_field(name='UV Index', value="{} Current index is **{}**.".format(uvresult, uvint), inline=True)
                if fio.has_alerts() is True:
                    em.add_field(name='Weather Alert', value=alertresult, inline=True)
                await ctx.send(embed=em)
            except Exception as fucking_hell:
                await ctx.send("```py\n{}\n```".format(fucking_hell))
        else:
            await ctx.send("Location isn't found or the given zip code or address is too short. Try again.")

    @commands.command()
    async def locate(self, ctx, *, address: str):
        """Go fucking stalk someone"""
        try:
            g = geocoder.google(address)
            loc = g.json
            var = json.dumps(loc)
            k = json.loads(var)
            if k['status'] == 'OK':
                yes = k['address']
            elif k['status'] == 'ZERO_RESULTS':
                yes = "There's no results found for this location."
            await ctx.send(yes)
        except Exception as e:
            await ctx.send("```py\n{}\n```".format(e))

def setup(bot):
    bot.add_cog(Weather(bot))
