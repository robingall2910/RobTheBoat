import traceback
import geocoder
import json
import discord
import datetime
import forecastio
import asyncio
import re

from discord.ext import commands
from utils.config import Config
from ipwhois import IPWhois
config = Config()

api_key = config._darksky_key
apikey = config._googleKey

def kms(func):
    def wrapped(*args, **kwargs):
        return func(wrapped, *args, **kwargs)
    return wrapped

class ówò(Exception):
    pass #i love you kirtus

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weather(self, ctx, *, addr: str):
        """Go check the weather out :^)"""
        try:
            #attempt to create a method
            @kms
            def getloc(this, addr):
                g = geocoder.google(addr, key=apikey)
                this.results = g.latlng
                this.loc = g.address
                this.data = g.json
            # variable setup
            getloc(addr)
            forecast = forecastio.load_forecast(api_key, getloc.results[0], getloc.results[1])
            c = forecast.currently()
            d = forecast.daily()
            a = forecast.alerts()
            m = forecast.minutely()
            em = discord.Embed(description="{}".format(d.summary))
            em.title = "Current weather for " + getloc.loc
            var = json.dumps(getloc.data)
            k = json.loads(var)
            #localization
            if ", USA" in getloc.loc:
                farenheit = True
            else:
                farenheit = False
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
                global a1
                global a2
                global alertresult1
                global alertresult2
                global whatever
                weatheralert = True
                a1 = a[0]
                #TODO: check for OS version when doing the time shit
                #no :)
                try:
                    if a[1] is not None:
                        try:
                            a2 = a[1]
                        except:
                            pass
                except IndexError:
                    a2 = None
                try:
                    if a[2] is not None:
                        try:
                            a3 = a[2]
                        except:
                            pass
                except IndexError:
                    a3 = None
                expiretime1 = datetime.datetime.fromtimestamp(int(a1.expires)).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')
                if a2 is not None:
                    expiretime2 = datetime.datetime.fromtimestamp(int(a2.expires)).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')
                if a3 is not None:
                    expiretime3 = datetime.datetime.fromtimestamp(int(a3.expires)).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')
                county = re.sub('([^\w]*County[^\w]*)+|[|\\^&\r\n]+', '', k['county'])
                # for future robin: if you want to add more alerts, divide 742 by amt total in alerts
                if county in a1.regions:
                    areas1 = k['county']
                else:
                    if len(a1.regions) > 2:
                        areasmod1 = ', '.join(a1.regions)
                        areas1 = areasmod1[:742] + ".."
                    else:
                        areas1 = ', '.join(a1.regions)
                try:
                    if county in a2.regions:
                        areas2 = k['county']
                    else:
                        if len(a2.regions) > 2:
                            areasmod2 = ', '.join(a2.regions)
                            areas2 = areasmod2[:371] + ".." #742
                            areas1 = areasmod1[:371] + ".."
                        else:
                            areas2 = ', '.join(a2.regions)
                except AttributeError:
                    pass
                try:
                    if county in a3.regions:
                        areas3 = k['county']
                    else:
                        if len(a3.regions) > 2:
                            areasmod3 = ', '.join(a3.regions)
                            areas3 = areasmod3[:247] + ".."
                            areas2 = areasmod2[:247] + ".."
                            areas1 = areasmod1[:247] + ".."
                        else:
                            areas3 = ', '.join(a3.regions)
                except AttributeError:
                    pass
                alertresult1 = "{} in {}. Expires {}. Click [here]({} 'National Weather Service/MET Office') for more information.".format(a1.title, areas1, expiretime1.rstrip(), a1.uri)
                if a2 is not None:
                    alertresult2 = "{} in {}. Expires {}. Click [here]({} 'National Weather Service/MET Office') for more information.".format(a2.title, areas2, expiretime2.rstrip(), a2.uri)
                if a3 is not None:
                    alertresult3 = "{} in {}. Expires {}. Click [here]({} 'National Weather Service/MET Office') for more information.".format(a3.title, areas3, expiretime3.rstrip(), a3.uri)
            except:
                print(traceback.format_exc())
                weatheralert = False
                a1 = None
                a2 = None
                a3 = None
                alertresult1 = None
                alertresult2 = None
                alertresult3 = None
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
            if c.uvIndex in (11, 12, 13, 14): #fuck going higher
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
                em.add_field(name='Weather Alert #1', value=alertresult1, inline=True)
            if a2 is not None:
                em.add_field(name='Weather Alert #2', value=alertresult2, inline=True)
            if a3 is not None:
                em.add_field(name='Weather Alert #3', value=alertresult3, inline=True)
            em.set_footer(text="Requested by: {} / Powered by Dark Sky".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
            if m.summary is not None:
                em.set_author(name=m.summary)
            await ctx.send(embed=em)
        #if anything breaks
        except TypeError as e:
            await ctx.send("The location was not found, please try again.")
            await ctx.send(e)

    @commands.command()
    async def locate(self, ctx, *, address: str):
        """Go fucking stalk someone"""
        try:
            @kms
            def getloc(this, address):
                g = geocoder.google(address, key=apikey)
                this.loc = g.json
            getloc(address)
            var = json.dumps(getloc.loc)
            k = json.loads(var)
            if k['ok'] is True:
                yes = discord.Embed(description=None)
                yes.title = 'Location Values'
                na = "Unknown"
                if ctx.me.color is not None:
                    yes.color = ctx.me.color
                else:
                    pass
                try:
                    yes.add_field(name='Address', value=k['address'], inline=True)
                except:
                    yes.add_field(name='Address', value=na, inline=True)
                try:
                    yes.add_field(name='City', value=k['city'], inline=True)
                except:
                    yes.add_field(name='City', value=na, inline=True)
                try:
                    yes.add_field(name='County', value=k['county'], inline=True)
                except:
                    yes.add_field(name='County', value=na, inline=True)
                try:
                    yes.add_field(name='Postal Code', value=k['postal'], inline=True)
                except:
                    yes.add_field(name='Postal Code', value=na, inline=True)
                try:
                    yes.add_field(name='Country', value=k['country'], inline=True)
                except:
                    yes.add_field(name='Country', value=na, inline=True)
                try:
                    yes.add_field(name='Admin Area Level 1', value=k['raw']['administrative_area_level_1']['long_name'], inline=True)
                except:
                    yes.add_field(name='Admin Area Level 1', value=na, inline=True)
                try:
                    yes.add_field(name='Admin Area Level 2', value=k['raw']['administrative_area_level_2']['long_name'], inline=True)
                except:
                    yes.add_field(name='Admin Area Level 2', value=na, inline=True)
                try:
                    yes.add_field(name='Locality', value=k['raw']['locality']['long_name'], inline=True)
                except:
                    yes.add_field(name='Locality', value=na, inline=True)
                try:
                    yes.add_field(name='Street Number', value=k['raw']['street_number']['long_name'], inline=True)
                except:
                    yes.add_field(name='Street Number', value=na, inline=True)
                try:
                    yes.add_field(name='Route (Road)', value=k['raw']['route']['long_name'], inline=True)
                except:
                    yes.add_field(name='Route (Road)', value=na, inline=True)
                try:
                    yes.add_field(name='State', value=k['state'], inline=True)
                except:
                    yes.add_field(name='State', value=na, inline=True)
                yes.add_field(name='Status', value=k['status'], inline=True)
                try:
                    yes.add_field(name='Accuracy and Confiedence Level', value='{}, {} out of 10'.format(k['accuracy'], k['confidence']), inline=True)
                except Exception as e:
                    yes.add_field(name='Accuracy and Confiedence Level', value=e, inline=True)
                    yes.set_footer(text="Requested by {}".format(ctx.author), icon_url=ctx.author.avatar_url)
            elif k['ok'] is False:
                yes = "There's no results found for this location."
            else:
                raise OSError #fuck you lol
            asyncio.sleep(15)
            await ctx.send(embed=yes)
        except Exception as e:
            await ctx.send("Error: {}".format(e))

    @commands.command()
    async def iplookup(self, ctx, *, ip: str):
        """Go stalk someone, but in IP"""
        try:
            obj = IPWhois(ip)
            res = obj.lookup_rdap()
            asn = res['asn_description']
            realip = res['query']
            g = geocoder.maxmind(ip)
            em = discord.Embed(description="Stalking someone™")
            em.title = "IP Lookup"
            em.add_field(name="IP", value=realip)
            em.add_field(name="Location", value=g.address + " " + g.postal)
            em.add_field(name="Company/ASN Number", value=asn)
            em.set_footer(text="Requested by: {}".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
            #color the sidebar
            if ctx.me.color == None:
                maybe = None
            else:
                maybe = ctx.me.color
            em.color = maybe
            await ctx.send(embed=em)
        except IndexError:
            await ctx.send("The IP didn't resolve anything, please try again.")


def setup(bot):
    bot.add_cog(Weather(bot))
