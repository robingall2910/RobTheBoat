import geocoder
import json
import discord
import datetime
import forecastio
import time
import asyncio

from discord.ext import commands
from utils.sharding import darkskyapi

api_key = darkskyapi

class Weather():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weather(self, ctx, *, addr: str):
        """Go check the weather out :^)"""
        try:
            # variable setup
            g = geocoder.google(addr)
            results = g.latlng
            loc = g.address
            forecast = forecastio.load_forecast(api_key, results[0], results[1])
            c = forecast.currently()
            d = forecast.daily()
            a = forecast.alerts()
            em = discord.Embed(description="{}".format(d.summary))
            #localization
            if ", USA" in loc:
                farenheit = True
            elif ", USA" not in loc:
                farenheit = False
            em.title = "Current Weather for {}".format(loc)
            # visibility
            try:
                visib = c.visibility
            except Exception:
                visib = "N/A"
            #color the sidebar
            if ctx.me.color == None:
                maybe = None
            else:
                maybe = ctx.me.color
            #weather alerts
            try:
                weatheralert = True
                a1 = a[0]
                expiretime = datetime.datetime.fromtimestamp(int(a1.expires)).strftime('%A %B %d, %Y at %I:%M %p')
                areas = ', '.join(a1.regions)
                alertresult = "{} in {}. Expires {}. Click [here]({} 'National Weather Service/MET Office') for more information.".format(a1.title, areas, expiretime, a1.uri)
            except Exception:
                weatheralert = False
            #uv index
            if c.uvIndex == 0:
                whatever = "**{}**. There's no light, or the sun is setting. Darkness is great.".format(c.uvIndex)
            if c.uvIndex in (1, 2):
                whatever = "**{}**. There's light, but it's eh.".format(c.uvIndex)
            if c.uvIndex in (3, 4, 5):
                whatever = "**{}**. Pretty sunny... Have fun outside.".format(c.uvIndex)
            if c.uvIndex in (6, 7):
                whatever = "**{}**. Plenty of sun! Wear sunscreen!.".format(c.uvIndex)
            if c.uvIndex in (8, 9, 10):
                whatever = "**{}**. I think it's starting get a bit too much. Get some shade from time to time.".format(c.uvIndex)
            if c.uvIndex in (11, 12, 13): #fuck going higher
                whatever = "**{}**. Definitely try to avoid the sunlight at the peak of day, unless you want to burn in hell.".format(c.uvIndex)
            #icon setup :)
            if c.icon == 'clear-day':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Sun.png')
            if c.icon == 'clear-night':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Moon.png')
            if c.icon == 'rain':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Rain.png')
            if c.icon == 'snow':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Snow.png')
            if c.icon == 'sleet':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Drizzle.png')
            if c.icon == 'wind':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Wind.png')
            if c.icon == 'fog':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Fog.png')
            if c.icon == 'cloudy':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud.png')
            if c.icon == 'partly-cloudy-day':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Sun.png')
            if c.icon == 'partly-cloudy-night':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Moon.png')
            if c.icon == 'thunderstorm':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Lightning.png')
            if c.icon == 'hail':
                em.set_thumbnail(url='https://dragonfire.me/climacons/Cloud-Hail.png')
            #here it begins
            if farenheit is True:
                em.add_field(name='Currently', value='{}°F'.format(c.temperature), inline=True)
                em.add_field(name='Wind Speed/Gust', value="{} mph/{} mph".format(c.windSpeed, c.windGust), inline=True)
                em.add_field(name='Visibility', value="{} miles".format(visib), inline=True)
            else:
                em.add_field(name='Currently', value='{}°C'.format(c.temperature), inline=True)
                em.add_field(name='Wind Speed/Gust', value="{} kph/{} kph".format(c.windSpeed, c.windGust), inline=True)
                em.add_field(name='Visibility', value="{} kilometers".format(visib), inline=True)
            em.color = maybe
            em.add_field(name='Humidity', value="{:.0%}".format(c.humidity), inline=True)
            em.add_field(name='UV Index', value=whatever, inline=True)
            if weatheralert is True:
                em.add_field(name='Weather Alert', value=alertresult, inline=True)
            em.set_footer(text="Powered by Dark Sky / Last updated: {}".format(time.strftime("%I:%M:%S %p %Z")), icon_url='https://darksky.net/images/darkskylogo.png')
            await ctx.send(embed=em)
        #if anything breaks
        except IndexError:
            await ctx.send("The location you provided was not found.")
        except Exception as e:
            await ctx.send("```py\n{}\n```".format(e))

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
            asyncio.sleep(15)
            await ctx.send(yes)
        except Exception as e:
            await ctx.send("```py\n{}\n```".format(e))

def setup(bot):
    bot.add_cog(Weather(bot))