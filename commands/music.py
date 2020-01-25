import asyncio
import discord
import youtube_dl

from discord.ext import commands

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options_earrape = {
    'options': '-vn -filter:a \"volume=120dB\"'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

earrape = False

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_search(cls, search, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        if earrape is True:
            cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options_earrape), data=data)
        else:
            cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.command()
    async def earrape(self, ctx):
        """enable earrape"""
        global earrape
        if earrape is False:
            earrape = True
            return await ctx.send("enabled earrape mode on next track")
        if earrape is True:
            earrape = False
            return await ctx.send("disabled earrape mode on next track")


    @commands.command(aliases=['summon', 'connect'])
    async def join(self, ctx):
        """connects bot to vc"""
        await ctx.author.voice.channel.connect()
        await ctx.send("i'm in")

    @commands.command()
    async def play(self, ctx, *, search):
        """plays a song"""
        await ctx.channel.trigger_typing()
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        source = await YTDLSource.from_search(search, stream=True)
        ctx.voice_client.play(source, after=lambda e: print('%s' % e) if e else None)
        requester = ctx.author
        await ctx.send('playing: ' + "**" + f"{source.title}" + "**" + ' requester: ' + "**" + f"{requester}" + "**")

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        """skips playing song"""
        ctx.voice_client.stop()
        await ctx.send('**' + f"{ctx.author}" + '**' + ' skipped the song')

    @commands.command(aliases=['vol', 'v'])
    async def volume(self, ctx, number: float):
        """changes the song volume"""
        ctx.voice_client.source.volume = number / 100
        await ctx.send("volume set to **{}**%".format(number))

    @commands.command()
    async def pause(self, ctx):
        """pauses the playing song"""
        ctx.voice_client.pause()
        await ctx.send("done paused")

    @commands.command()
    async def resume(self, ctx):
        """resumes playing the paused song"""
        ctx.voice_client.resume()
        await ctx.send("done resumed")

    @commands.command(aliases=['disconnect', 'stop'])
    async def leave(self, ctx):
        """disconnects bot from vc"""
        await ctx.voice_client.disconnect()
        await ctx.send("ok bye")


def setup(client):
    client.add_cog(Music(client))
