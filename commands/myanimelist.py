import xml.sax.saxutils as saxutils

from xml.dom import minidom
from xml.parsers import expat as XmlParserErrors
from discord.ext import commands
from utils.logger import log
from utils.config import Config
from utils.tools import *
config = Config()

class MyAnimeList():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def anime(self, ctx, *, name:str):
        """Searches MyAnimeList for the specified anime"""
        await self.bot.send_typing(ctx.message.channel)
        r = requests.get("https://myanimelist.net/api/anime/search.xml?q={}".format(name), auth=requests.auth.HTTPBasicAuth(config._malUsername, config._malPassword))
        if r.status_code == 401:
            log.critical("The MyAnimeList credinals are incorrect, please check your MyAnimeList login information in the config.")
            await self.bot.say("The MyAnimeList credinals are incorrect, contact the bot developer!")
            return
        with open("data/anime.xml", "wb") as xml:
            xml.write(r.content)
        try:
            xmldoc = minidom.parse("data/anime.xml")
        except XmlParserErrors.ExpatError:
            await self.bot.say("Couldn't find any anime named `{}`".format(name))
            return
        # pls no flame
        anime = xmldoc.getElementsByTagName("entry")[0]
        id = anime.getElementsByTagName("id")[0].firstChild.nodeValue
        title = anime.getElementsByTagName("title")[0].firstChild.nodeValue
        try:
            english = anime.getElementsByTagName("english")[0].firstChild.nodeValue
        except:
            english = title
        episodes = anime.getElementsByTagName("episodes")[0].firstChild.nodeValue
        score = anime.getElementsByTagName("score")[0].firstChild.nodeValue
        type = anime.getElementsByTagName("type")[0].firstChild.nodeValue
        status = anime.getElementsByTagName("status")[0].firstChild.nodeValue
        start_date = anime.getElementsByTagName("start_date")[0].firstChild.nodeValue
        end_date = anime.getElementsByTagName("end_date")[0].firstChild.nodeValue
        synopsis = saxutils.unescape(anime.getElementsByTagName("synopsis")[0].firstChild.nodeValue)
        synopsis = remove_html(synopsis)
        print(len(synopsis))
        if len(synopsis) > 500:
            synopsis = synopsis[:500] + "..."
        url = "https://myanimelist.net/anime/{}".format(id)
        msg = "```Title: {}\nEnglish title: {}\nEpisodes: {}\nScore: {}\nType: {}\nStatus: {}\nStart date: {}\nEnd Date: {}```{}\nRead more: {}".format(title, english, episodes, score, type, status, start_date, end_date, synopsis, url)
        await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def manga(self, ctx, *, name:str):
        """Searches MyAnimeList for the specified manga"""
        await self.bot.send_typing(ctx.message.channel)
        r = requests.get("https://myanimelist.net/api/manga/search.xml?q={}".format(name), auth=requests.auth.HTTPBasicAuth(config._malUsername, config._malPassword))
        if r.status_code == 401:
            log.critical("The MyAnimeList credinals are incorrect, please check your MyAnimeList login information in the config.")
            await self.bot.say("The MyAnimeList credinals are incorrect, contact the bot developer!")
            return
        with open("data/manga.xml", "wb") as xml:
            xml.write(r.content)
        try:
            xmldoc = minidom.parse("data/manga.xml")
        except XmlParserErrors.ExpatError:
            await self.bot.say("Couldn't find any manga named `{}`".format(name))
            return
        # pls no flame
        anime = xmldoc.getElementsByTagName("entry")[0]
        id = anime.getElementsByTagName("id")[0].firstChild.nodeValue
        title = anime.getElementsByTagName("title")[0].firstChild.nodeValue
        try:
            english = anime.getElementsByTagName("english")[0].firstChild.nodeValue
        except:
            english = title
        chapters = anime.getElementsByTagName("chapters")[0].firstChild.nodeValue
        volumes = anime.getElementsByTagName("volumes")[0].firstChild.nodeValue
        score = anime.getElementsByTagName("score")[0].firstChild.nodeValue
        type = anime.getElementsByTagName("type")[0].firstChild.nodeValue
        status = anime.getElementsByTagName("status")[0].firstChild.nodeValue
        start_date = anime.getElementsByTagName("start_date")[0].firstChild.nodeValue
        end_date = anime.getElementsByTagName("end_date")[0].firstChild.nodeValue
        url = "https://myanimelist.net/manga/{}".format(id)
        msg = "```Title: {}\nEnglish title: {}\nChapters: {}\nVolumes: {}\nScore: {}\nType: {}\nStatus: {}\nStart date: {}\nEnd Date: {}```\nRead more: {}".format(title, english, chapters, volumes, score, type, status, start_date, end_date, url)
        await self.bot.say(msg)

def setup(bot):
    bot.add_cog(MyAnimeList(bot))
