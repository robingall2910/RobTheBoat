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
        nsfw = discord.utils.get(ctx.message.server.me.roles, name="NSFW")
        nsfw_channel_name = read_data_entry(ctx.message.server.id, "nsfw-channel")
        if not ctx.message.channel.name == nsfw_channel_name:
            if not nsfw:
                await self.bot.say("I need the so called NSFW role for anything outside of the `{}` channel. Keep them eyes clean for others.".format(nsfw_channel_name))
                return
        await self.bot.send_typing(ctx.message.channel)
        download_file("http://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={}&tags={}".format(limit, tags), "data/rule34.json")
        with open("data/rule34.json", encoding="utf8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                await self.bot.say("Well shit. No results. I know you need it though. Requested tags: `{}`".format(tags))
                return

        count = len(data)
        if count == 0:
            await self.bot.say("Nope. No results. Requested tags: `{}`".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            image = data[random.randint(0, count)]
            images.append("http://img.rule34.xxx/images/{}/{}".format(image["directory"], image["image"]))
        await self.bot.say("Displaying heaps amount of porn. Showing {} out of {} for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

    @commands.command(pass_context=True)
    async def e621(self, ctx, *, tags:str):
        """Searches e621.net for the specified tagged images"""
        nsfw = discord.utils.get(ctx.message.server.me.roles, name="NSFW")
        nsfw_channel_name = read_data_entry(ctx.message.server.id, "nsfw-channel")
        if not ctx.message.channel.name == nsfw_channel_name:
            if not nsfw:
                await self.bot.say("Henlo furry. You need to give me the NSFW role for anything outside of the `{}` channel. Other than that, go back in there anyway.".format(nsfw_channel_name))
                return
        await self.bot.send_typing(ctx.message.channel)
        download_file("https://e621.net/post/index.json?limit={}&tags={}".format(limit, tags), "data/e621.json")
        with open("data/e621.json", encoding="utf8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                await self.bot.say("DAMN, NO RESULTS FOR FUCKING `{}`".format(tags))
                return
        count = len(data)
        if count == 0:
            await self.bot.say("SORRY BUT THE TAGS `{}` ARENT AVAILABLE TOGETHER?".format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            images.append(data[random.randint(0, count)]["file_url"])
        await self.bot.say("Displaying heaps amount of porn. Showing {} out of {} for `{}`\n{}".format(image_count, count, tags, "\n".join(images)))

    @commands.command(pass_context=True)
    async def yandere(self, ctx, *, tags:str):
        """Searches yande.re for the specified tagged images"""
        nsfw = discord.utils.get(ctx.message.server.me.roles, name="NSFW")
        nsfw_channel_name = read_data_entry(ctx.message.server.id, "nsfw-channel")
        if not ctx.message.channel.name == nsfw_channel_name:
            if not nsfw:
                await self.bot.say("I must have the \"NSFW\" role in order to use that command in other channels that are not named `{}`".format(nsfw_channel_name))
                return
        await self.bot.send_typing(ctx.message.channel)
        download_file("https://yande.re/post/index.json?limit={}&tags={}".format(limit, tags), "data/yandere.json")
        with open("data/yandere.json", encoding="utf8") as file:
            try:
                data = json.load(file)
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
        nsfw = discord.utils.get(ctx.message.server.me.roles, name="NSFW")
        nsfw_channel_name = read_data_entry(ctx.message.server.id, "nsfw-channel")
        if not ctx.message.channel.name == nsfw_channel_name:
            if not nsfw:
                await self.bot.say("I must have the \"NSFW\" role in order to use that command in other channels that are not named `{}`".format(nsfw_channel_name))
                return
        await self.bot.send_typing(ctx.message.channel)
        download_file("http://danbooru.donmai.us/post/index.json?limit={}&tags={}".format(limit, tags), "data/danbooru.json")
        with open("data/danbooru.json", encoding="utf8") as file:
            try:
                data = json.load(file)
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


def setup(bot):
    bot.add_cog(NSFW(bot))
