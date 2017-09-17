# encoding=utf8
import asyncio
import cat
import random
import os
import json
import urllib.request
import wikipedia
import time
import sys

from cleverwrap import CleverWrap
from utils.config import Config
from discord.ext import commands
from utils.tools import *
from utils.unicode import *
from utils.fun.lists import *

class Fuckery():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, message:str):
        """Make the bot say whatever you want it to say"""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if ctx.author is not ctx.author.bot:
            await ctx.send(message.replace("@everyone", "everyone"))
        else:
            return

    @commands.command()
    async def test(self, ctx):
        """No context."""
        await ctx.send("( ͡° ͜ʖ ͡°) I love you")

    @commands.command()
    async def cat(self, ctx):
        """Sends a random cute cat gifs because cats are soooo cuteeee <3 >.< -Seth, 2016"""
        await ctx.channel.trigger_typing()
        cat.getCat(directory="data", filename="cat", format="gif")
        await asyncio.sleep(1) # This is so the bot has enough time to download the file
        await ctx.send(file=discord.File("data/cat.gif"))
        # Watch Nero spam this command until the bot crashes

    @commands.command()
    async def f(self, ctx):
        """Press F to pay your respects"""
        await ctx.send("Guess what? {} just paid their respects! Amount paid: {}".format(ctx.author, random.randint(0, 10000)))

    @commands.command()
    async def nicememe(self, ctx):
        """Nice Meme!"""
        await ctx.send("http://niceme.me")

    @commands.command()
    async def dab(self, ctx):
        """Dab for me squiddy"""
        await ctx.send("http://i.giphy.com/lae7QSMFxEkkE.gif")

    @commands.command()
    async def rekt(self, ctx):
        """#REKT"""
        await ctx.channel.trigger_typing()
        await ctx.send(file=discord.File("assets/imgs/rekt.gif"))

    @commands.command()
    async def roasted(self, ctx):
        """MY NIGGA YOU JUST GOT ROASTED!"""
        await ctx.channel.trigger_typing()
        await ctx.send(file=discord.File("assets/imgs/roasted.gif"))

    @commands.command()
    async def yiffinhell(self, ctx):
        """snek yiff"""
        await ctx.channel.trigger_typing()
        await ctx.send(file=discord.File("assets/imgs/yiffinhell.png"))

    @commands.command()
    async def spam(self, ctx):
        """SPAM SPAM SPAM"""
        await ctx.channel.trigger_typing()
        await ctx.send(file=discord.File("assets/imgs/spam.png"))

    @commands.command()
    async def internetrules(self, ctx):
        """The rules of the internet"""
        await ctx.channel.trigger_typing()
        #this is how you create a memory leak
        print("attempted to try " + sys.getdefaultencoding())
        gayrule = random.choice(open('assets/InternetRules.txt', encoding="utf8").readlines())
        await ctx.send(gayrule)

    @commands.command()
    async def perf(self):
        """the return of the furry bullshit"""
        rt = random.choice(tweetsthatareokhand)
        ctx.send(rt)

    @commands.command()
    async def santropez(self, ctx):
        """:~)"""
        yes = [
        ":~)",
        ":~)",
        ":-)",
        ":^)",
        ":)",
        ":'~)",
        ":racehorse:",
        ":horse",
        "(:",
        "pppppppppppppbbbbbbbbbbbbbbbbbbbbbbbbbbbbhhhhhhhhhhhhhhhhhhhhhhtttttttttttttttttttt",
        "pppppppppppppppppppppppppppppppppppppppppppppppppppppppbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhtttttttttttttttttttt",
        "I SPIT ON YOU.",
        "Nine nine nine",
        ":drum: :racehorse:",
        ":french_bread:",
        ":duck:",
        "spt",
        "spt2",
        "ssssssssssssssssssssspppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppptttttttttttttttttttttttttt"
        ]
        sppt = random.choice(yes)
        if sppt == "spt":
            await ctx.send(file=discord.File("assets/imgs/spt.png"))
        if sppt == "spt2":
            await ctx.send(file=discord.File("assets/imgs/spt2.png"))
        await ctx.send(random.choice(yes))

    @commands.command()
    async def quote(self, ctx):
        """Don't quote me on that"""
        await ctx.channel.trigger_typing()
        await ctx.send(file=discord.File("assets/imgs/quotes/{}.png".format(random.randint(1, len([file for file in os.listdir("assets/imgs/quotes")])))))

    @commands.command()
    async def delet(self, ctx):
        """Delet this"""
        await ctx.channel.trigger_typing()
        await ctx.send(file=discord.File("assets/imgs/delet_this.jpg"))

    @commands.command()
    async def roll(self, ctx, sides: int):
        """Roll the fuck out of this shit."""
        rolling = random.randint(1, sides)
        await ctx.send("You got a {} out of the {} sided die.".format(rolling, str(sides)))

    @commands.command()
    async def lenny(self, ctx):
        """<Insert lenny face here>"""
        await ctx.send(lenny)
        #they're back fuck yeah
        
    @commands.command()
    async def psat(self, ctx):
        """Please."""
        await ctx.send(random.choice(psat_memes))

    @commands.command(name="8ball")
    async def ball(self, ctx, *, question:str):
        """It's just python random don't take it seriously kthx"""
        await ctx.send("{}: {}".format(ctx.author.name, random.choice(magic_conch_shell)))

    @commands.command()
    async def insult(self, ctx, *, user:str):
        """Insult those ass wipes"""
        if user is "@everyone" or "@here":
            result = user.strip('<@>')
        else:
            result = user
        await ctx.send("{} {}".format(result, random.choice(insults)))

    @commands.command()
    async def compliment(self, ctx):
        """I love you."""
        await ctx.send("{}".format(random.choice(compliments)))

    @commands.command()
    async def actdrunk(self, ctx):
        """I got drunk on halloween in 2016 it was great"""
        await ctx.send(random.choice(drunkaf))

    @commands.command()
    async def talk(self, ctx, *, pussy:str):
        """talk to the bot"""
        config = Config()
        api_key = config.cb_api_key
        cw = CleverWrap(api_key)
        themessage = cw.say(pussy)
        result = themessage.encode(encoding='UTF-8')
        try:
            await ctx.send(str(ctx.author) + " >> " + cw.say(result))
        except UnicodeDecodeError:
            await ctx.send("Error has occured trying to decode the Cleverbot message.")

    @commands.command()
    async def ship(self, ctx, user1:discord.User=None, user2:discord.User=None):
        """Treat yourself to shipping to FedEx, DHL, UPS, USPS, and more. Nah not really. Ship yourself with someone if you could."""
        if user2 is None:
            await ctx.send("I see you haven't shipped yourself with anyone. Sad.")
        else:
            await ctx.send("I hereby ship {} and {} officially by bot code.".format(user1.mention, user2.mention))

    @commands.command()
    async def rate(self, ctx, *, user):
        """Have the bot rate yourself or another user"""
        if user is None:
            await ctx.send("I rate you a `{}`/`10`".format(random.randint(0, 10)))
        else:
            await ctx.send("I rate {} a `{}`/`10`".format(user, random.randint(0, 10)))

    @commands.command()
    async def coinflip(self, ctx):
        """Make the bot flip either heads or tails."""
        result = random.randint(0, 1)
        if result == int(0):
            await ctx.send("You flipped a coin as high as you could. It falls on the floor since you can't catch it. Surprise, it's heads!")
        elif result == int(1):
            await ctx.send("You flip the coin. You catch it somehow, and interestingly enough, it's tails!")

    @commands.command()
    async def wiki(self, ctx, *, query: str):
        """
        Search the infinite pages of wikipedia!
        """
        #Holy fucking shit, how long has that mistake been here?
        cont2 = query
        cont = re.sub(r"\s+", '_', query)
        q = wikipedia.page(cont)
        await ctx.channel.trigger_typing()
        await ctx.send("{}:\n```\n{}\n```\nFor more information, visit <{}>".format(q.title,
                                                                                                              wikipedia.summary(
                                                                                                                  query,
                                                                                                                  sentences=5),
                                                                                                              q.url))
        await ctx.send(cont)
        if wikipedia.exceptions.PageError == True:
            await ctx.send("Error 404. Try another.")
        elif wikipedia.exceptions.DisambiguationError == True:
            await ctx.send("Too many alike searches, please narrow it down more...")

    @commands.command()
    async def time(self, ctx):
        """Tells the current time from the server"""
        d = time.strftime("%A, %B %d, %Y")
        t = time.strftime("%I:%M:%S %p %Z")
        linemedaddy = "```ruby\n Current Date: " + d + '\n Current Time: ' + t + "\n" + "```"
        await ctx.send(linemedaddy)

    @commands.command()
    async def markov(self, ctx):
        """A big failure on trying to copy what I say"""
        markov = open('markovrobin.txt').read().splitlines()
        somethingsudden = random.choice(markov)
        await ctx.send(somethingsudden)


    @commands.command()
    async def memegen(self, ctx, template: str, *, lines: str):
        """
        Attempt on trying to create a meme command, .memeg (template/line1/line2)
        List: http://memegen.link/templates/
        """
        if len(template) and len(lines) != 0:
            memeg = str(template) + " " + str(lines)
            await ctx.send("http://memegen.link/" + re.sub(r"\s+", '-', memeg) + ".jpg")
        else:
            await ctx.send("You didn't enter a message. Templates: http://memegen.link/templates/")

    @commands.command()
    async def honk(self, ctx):
        """Honk honk mother fucker. yes this came back lukkan."""
        await ctx.send(random.choice(honkhonkfgt))

    @commands.command()
    async def plzmsgme(self, ctx, *, message:str):
        """Seriously, why the fuck are you doing this to yourself?"""
        await ctx.author.dm_channel.send(message)
        await ctx.send(":ok_hand: check your DMs")

    @commands.command()
    async def lameme(self, ctx):
        """la meme my bro xdddddddddddddddddd"""
        await ctx.channel.trigger_typing()
        await ctx.send("la meme xd xd")
        await ctx.send(file=discord.File( "assets/imgs/lameme.jpg"))

    @commands.command()
    async def quote(self, ctx, id:int):
        """Quotes a message with the specified message ID"""
        message = await ctx.channel.get_message(id)
        if message is None:
            await ctx.send("Can't find {} in here.".format(id))
            return
        embed = make_message_embed(message.author, message.author.color, message.content, formatUser=True)
        await ctx.send(None, embed=embed)

def setup(bot):
    bot.add_cog(Fuckery(bot))
