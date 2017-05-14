import asyncio
import cat
import random
import os
import json
import urllib.request
import wikipedia
import time

from cleverwrap import CleverWrap
from utils.config import Config
from discord.ext import commands
from utils.tools import *
from utils.unicode import *
from utils.fun.lists import *

class Fuckery():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def say(self, ctx, *, message:str):
        """Make the bot say whatever you want it to say"""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if ctx.message.author is not ctx.message.author.bot:
            await self.bot.say(message.replace("@everyone", "everyone"))
        else:
            return

    @commands.command(pass_context=True)
    async def test(self, ctx):
        """No context."""
        await self.bot.say("( ͡° ͜ʖ ͡°) I love you")

    @commands.command(pass_context=True)
    async def cat(self, ctx):
        """Sends a random cute cat gifs because cats are soooo cuteeee <3 >.< -Seth, 2016"""
        await self.bot.send_typing(ctx.message.channel)
        cat.getCat(directory="data", filename="cat", format="gif")
        await asyncio.sleep(1) # This is so the bot has enough time to download the file
        await self.bot.send_file(ctx.message.channel, "data/cat.gif")
        # Watch Nero spam this command until the bot crashes

    @commands.command(pass_context=True)
    async def f(self, ctx):
        """Press F to pay your respects"""
        await self.bot.say("Guess what? {} just paid their respects! Amount paid: {}".format(ctx.message.author, random.randint(1, 10000)))

    @commands.command()
    async def nicememe(self):
        """Nice Meme!"""
        await self.bot.say("http://niceme.me")

    @commands.command()
    async def dab(self):
        """Dab for me squiddy"""
        await self.bot.say("http://i.giphy.com/lae7QSMFxEkkE.gif")

    @commands.command(pass_context=True)
    async def rekt(self, ctx):
        """#REKT"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/rekt.gif")

    @commands.command(pass_context=True)
    async def roasted(self, ctx):
        """MY NIGGA YOU JUST GOT ROASTED!"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/roasted.gif")

    @commands.command(pass_context=True)
    async def yiffinhell(self, ctx):
        """snek yiff"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/yiffinhell.png")

    @commands.command(pass_context=True)
    async def spam(self, ctx):
        """SPAM SPAM SPAM"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/spam.png")

    @commands.command(pass_context=True)
    async def internetrules(self, ctx):
        """The rules of the internet"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/InternetRules.txt")

    @commands.command(pass_context=True)
    async def quote(self, ctx):
        """Don't quote me on that"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/quotes/{}.png".format(random.randint(1, len([file for file in os.listdir("assets/imgs/quotes")]))))

    @commands.command(pass_context=True)
    async def delet(self, ctx):
        """Delet this"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/delet_this.jpg")

    @commands.command(pass_context=True)
    async def roll(self, ctx, sides: int):
        """Roll the fuck out of this shit."""
        rolling = random.randint(1, sides)
        await self.bot.say("You got a {} out of the {} sided die.".format(rolling, str(sides)))

    @commands.command()
    async def lenny(self):
        """<Insert lenny face here>"""
        await self.bot.say(lenny)
        #they're back fuck yeah
        
    @commands.command()
    async def psat(self):
        #Please.
        await self.bot.say(random.choice(psat_memes))

    @commands.command(pass_context=True, name="8ball")
    async def ball(self, ctx, *, question:str):
        """It's just python random don't take it seriously kthx"""
        await self.bot.say("{}: {}".format(ctx.message.author.name, random.choice(magic_conch_shell)))

    @commands.command()
    async def insult(self, *, user:str):
        """Insult those ass wipes"""
        await self.bot.say("{} {}".format(user, random.choice(insults)))

    @commands.command()
    async def compliment(self):
        """I love you."""
        await self.bot.say("{}".format(random.choice(compliments)))

    @commands.command()
    async def actdrunk(self):
        """I got drunk on halloween in 2016 it was great"""
        await self.bot.say(random.choice(drunkaf))

    @commands.command(pass_context=True)
    async def talk(self, ctx, *, pussy:str):
        """talk to the bot"""
        config = Config()
        api_key = config.cb_api_key
        cw = CleverWrap(api_key)
        await self.bot.say(str(ctx.message.author) + " >> " + cw.say(pussy))

    @commands.command()
    async def ship(self, user1:discord.User=None, user2:discord.User=None):
        """Treat yourself to shipping to FedEx, DHL, UPS, USPS, and more. Nah not really. Ship yourself with someone if you could."""
        if user2 is None:
            await self.bot.say("I see you haven't shipped yourself with anyone. Sad.")
        else:
            await self.bot.say("I hereby ship {} and {} officially by bot code.".format(user1.mention, user2.mention))

    @commands.command()
    async def rate(self, *, user):
        """Have the bot rate yourself or another user"""
        if user is None:
            await self.bot.say("I rate you a `{}`/`10`".format(random.randint(0, 10)))
        else:
            await self.bot.say("I rate {} a `{}`/`10`".format(user, random.randint(0, 10)))

    @commands.command(pass_context=True)
    async def wiki(self, ctx, *, query: str):
        """
        Search the infite pages!
        """
        cont2 = query
        cont = re.sub(r"\s+", '_', query)
        q = wikipedia.page(cont)
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_message(ctx.message.channel, "{}:\n```\n{}\n```\nFor more information, visit <{}>".format(q.title,
                                                                                                              wikipedia.summary(
                                                                                                                  query,
                                                                                                                  sentences=5),
                                                                                                              q.url))
        await self.bot.send_message(ctx.message.channel, cont)
        if wikipedia.exceptions.PageError == True:
            await self.bot.send_message(ctx.message.channel, "Error 404. Try another.")
        elif wikipedia.exceptions.DisambiguationError == True:
            await self.bot.send_message(ctx.message.channel, "Too many alike searches, please narrow it down more...")

    @commands.command(pass_context=True)
    async def time(self, ctx):
        d = time.strftime("%A, %B %d, %Y")
        t = time.strftime("%I:%M:%S %p %Z")
        linemedaddy = "```ruby\n Current Date: " + d + '\n Current Time: ' + t + "\n" + "```"
        await self.bot.send_message(ctx.message.channel, linemedaddy)

    @commands.command(pass_context=True)
    async def markov(self, ctx):
        markov = open('markovrobin.txt').read().splitlines()
        somethingsudden = random.choice(markov)
        await self.bot.say(somethingsudden)


    @commands.command(pass_context=True)
    async def memegen(self, ctx, template: str, *, lines: str):
        """
        Attempt on trying to create a meme command, .memeg (template/line1/line2)
        List: http://memegen.link/templates/
        """
        if len(template) and len(lines) != 0:
            memeg = str(template) + " " + str(lines)
            await self.bot.say("http://memegen.link/" + re.sub(r"\s+", '-', memeg) + ".jpg")
        else:
            await self.bot.say("You didn't enter a message. Templates: http://memegen.link/templates/")

    @commands.command()
    async def honk(self):
        """Honk honk mother fucker. yes this came back lukkan."""
        await self.bot.say(random.choice(honkhonkfgt))

    @commands.command(pass_context=True)
    async def plzmsgme(self, ctx, *, message:str):
        """Seriously, why the fuck are you doing this to yourself?"""
        await self.bot.send_message(ctx.message.author, message)
        await self.bot.say(":ok_hand: check your DMs")

    @commands.command(pass_context=True)
    async def lameme(self, ctx):
        """la meme my bro xdddddddddddddddddd"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_message(ctx.message.channel, "la meme xd xd")
        await self.bot.send_file(ctx.message.channel, "assets/imgs/lameme.jpg")

    @commands.command(pass_context=True)
    async def quote(self, ctx, id:str):
        """Quotes a message with the specified message ID"""
        message = await self.bot.get_message(ctx.message.channel, id)
        if message is None:
            await self.bot.say("Can't find {} in here.".format(id))
            return
        embed = make_message_embed(message.author, message.author.color, message.content, formatUser=True)
        await self.bot.say(None, embed=embed)

def setup(bot):
    bot.add_cog(Fuckery(bot))
