import random
import json

from discord.ext import commands
from utils.tools import *
from utils.mysql import *
from utils.config import Config
config = Config()

# This is the limit to how many posts are selected
limit = config.max_nsfw_count

class NSFW():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def rule34(self, ctx, *, tags:str):
        """Searches rule34.xxx for the specified tagged images"""
        if not ctx.message.channel.name == "nsfw" and not ctx.message.channel.name.startswith("nsfw-"):
            await self.bot.say("This is not an NSFW channel. NSFW channels must be named `nsfw` or must start with `nsfw-`.")
            return
        await self.bot.send_typing(ctx.message.channel)
        try:
            data = json.loads(requests.get("http://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={}&tags={}".format(limit, tags)).text)
        except json.JSONDecodeError:
            await self.bot.say("No results found for `{}`".format(tags))
            return

        count = len(data)
        if count == 0:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            image = data[random.randint(0, count)]
            images.append("http://img.rule34.xxx/images/{}/{}".format(image["directory"], image["image"]))
        await self.bot.say("Showing {} out of {} results for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

    @commands.command(pass_context=True)
    async def e621(self, ctx, *, tags:str):
        """Searches e621.net for the specified tagged images"""
        if not ctx.message.channel.name == "nsfw" and not ctx.message.channel.name.startswith("nsfw-"):
            await self.bot.say("This is not an NSFW channel. NSFW channels must be named `nsfw` or must start with `nsfw-`.")
            return
        await self.bot.send_typing(ctx.message.channel)
        try:
            data = json.loads(requests.get("https://e621.net/post/index.json?limit={}&tags={}".format(limit, tags)).text)
        except json.JSONDecodeError:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        count = len(data)
        if count == 0:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            images.append(data[random.randint(0, count)]["file_url"])
        await self.bot.say("Showing {} out of {} results for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

    @commands.command(pass_context=True)
    async def yandere(self, ctx, *, tags:str):
        """Searches yande.re for the specified tagged images"""
        if not ctx.message.channel.name == "nsfw" and not ctx.message.channel.name.startswith("nsfw-"):
            await self.bot.say("This is not an NSFW channel. NSFW channels must be named `nsfw` or must start with `nsfw-`.")
            return
        await self.bot.send_typing(ctx.message.channel)
        try:
            data = json.loads(requests.get("https://yande.re/post/index.json?limit={}&tags={}".format(limit, tags)).text)
        except json.JSONDecodeError:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        count = len(data)
        if count == 0:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            images.append(data[random.randint(0, count)]["file_url"])
        await self.bot.say("Showing {} out of {} results for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

    @commands.command(pass_context=True)
    async def danbooru(self, ctx, *, tags:str):
        """Searches danbooru.donmai.us for the specified tagged images"""
        if not ctx.message.channel.name == "nsfw" and not ctx.message.channel.name.startswith("nsfw-"):
            await self.bot.say("This is not an NSFW channel. NSFW channels must be named `nsfw` or must start with `nsfw-`.")
            return
        await self.bot.send_typing(ctx.message.channel)
        try:
            data = json.loads(requests.get("https://danbooru.donmai.us/post/index.json?limit={}&tags={}".format(limit, tags)).text)
        except json.JSONDecodeError:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        count = len(data)
        if count == 0:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            try:
                images.append("http://danbooru.donmai.us{}".format(data[random.randint(0, count)]["file_url"]))
            except KeyError:
                await self.bot.say(data["message"])
                return
        await self.bot.say("Showing {} out of {} results for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

    @commands.command(pass_context=True)
    async def gelbooru(self, ctx, *, tags:str):
        """Searches gelbooru.com for the specified tagged images"""
        if not ctx.message.channel.name == "nsfw" and not ctx.message.channel.name.startswith("nsfw-"):
            await self.bot.say("This is not an NSFW channel. NSFW channels must be named `nsfw` or must start with `nsfw-`.")
            return
        await self.bot.send_typing(ctx.message.channel)
        try:
            data = json.loads(requests.get("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={}&tags={}".format(limit, tags)).text)
        except json.JSONDecodeError:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        count = len(data)
        if count == 0:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            try:
                images.append("http:{}".format(data[random.randint(0, count)]["file_url"]))
            except KeyError:
                await self.bot.say(data["message"])
                return
        await self.bot.say("Showing {} out of {} results for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

    @commands.command(pass_context=True)
    async def xbooru(self, ctx, *, tags: str):
        """Searches xbooru.com for the specified tagged images"""
        if not ctx.message.channel.name == "nsfw" and not ctx.message.channel.name.startswith("nsfw-"):
            await self.bot.say("This is not an NSFW channel. NSFW channels must be named `nsfw` or must start with `nsfw-`.")
            return
        await self.bot.send_typing(ctx.message.channel)
        try:
            data = json.loads(requests.get("https://xbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={}&tags={}".format(limit, tags)).text)
        except json.JSONDecodeError:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        count = len(data)
        if count == 0:
            await self.bot.say("No results found for `{}`".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            try:
                post = data[random.randint(0, count)]
                images.append("http://img3.xbooru.com/images/{}/{}".format(post["directory"], post["image"]))
            except KeyError:
                await self.bot.say(data["message"])
                return
        await self.bot.say("Showing {} out of {} results for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

def setup(bot):
    bot.add_cog(NSFW(bot))
