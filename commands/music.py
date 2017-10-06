import asyncio
import traceback
import os
import shutil
import youtube_dl

from discord.ext import commands
from utils.mysql import *
from utils.logger import log
from utils.opus_loader import load_opus_lib
from utils.config import Config;
from utils import checks

load_opus_lib()
config = Config()

ytdl_format_options = {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3", "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": False, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0", "preferredcodec": "libmp3lame"}

def get_ytdl(id):
    format = ytdl_format_options
    format["outtmpl"] = "data/music/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)

class Song():
    def __init__(self, entry, path, title, duration, requester):
        self.entry = entry
        self.path = path
        self.title = title
        self.duration = duration
        self.requester = requester
        if self.duration:
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            self.duration = "%02d:%02d:%02d" % (h, m, s)

    def __str__(self):
        return "**{}** `[{}]`".format(self.title, self.duration)

    def title_with_requester(self):
        return "{} ({})".format(self.__str__(), self.requester)


class Queue():
    def __init__(self, bot, voice_client, text_channel):
        self.bot = bot
        self.voice_client = voice_client
        self.text_channel = text_channel
        self.play_next_song = asyncio.Event()
        self.song_list = []
        self.current = None
        self.songs = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_change_task())
        self.skip_votes = []

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set())

    async def audio_change_task(self):
        while True:
            log.debug("Change task ran")
            self.play_next_song.clear()
            log.debug("clear af")
            if self.current and not self.current.path in [song.path for song in self.song_list]:
                os.remove(self.current.path)
            self.current = await self.songs.get()
            self.song_list.remove(str(self.current))
            self.skip_votes.clear()
            await self.text_channel.send("Now playing {}".format(self.current.title_with_requester()))
            self.voice_client.play(self.current.entry, after=lambda e: self.play_next_song.set())
            log.debug("k")
            await self.play_next_song.wait()
            log.debug("it pass")

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, ctx):
        queue = self.queues.get(ctx.guild.id)
        if queue is None:
            queue = Queue(self.bot, ctx.voice_client, ctx.channel)
            self.queues[ctx.guild.id] = queue
        return queue

    async def disconnect_all_voice_clients(self):
        queues = self.queues
        for id in queues:
            try:
                await self.queues[id].voice_client.disconnect()
                self.clear_data(id)
                del self.queues[id]
            except:
                pass

    @staticmethod
    def clear_data(id=None):
        if id is None:
            shutil.rmtree("data/music")
        else:
            shutil.rmtree("data/music/{}".format(id))

    @staticmethod
    def download_video(ctx, url):
        ytdl = get_ytdl(ctx.guild.id)
        data = ytdl.extract_info(url, download=True)
        if "entries" in data:
            data = data["entries"][0]
        title = data["title"]
        id = data["id"]
        duration = None
        # Some things like directly playing an audio file might not have duration data
        try:
            duration = data["duration"]
        except KeyError:
            pass
        path = "data/music/{}".format(ctx.guild.id)
        filepath = "{}/{}.mp3".format(path, id)
        entry = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filepath))
        # if the volume is too high it will sound like ear rape
        entry.volume = 0.4
        song = Song(entry, path, title, duration, ctx.author)
        return song

    @commands.command()
    async def summon(self, ctx):
        await ctx.send("Please use {}play as it will automatically connect the bot to the voice channel if it isn't already in it.")

    @commands.command()
    async def play(self, ctx, *, url:str):
        """Enqueues a song to be played"""
        await ctx.channel.trigger_typing()
        if ctx.voice_client is None:
            if ctx.author.voice.channel:
                try:
                    await ctx.author.voice.channel.connect()
                except discord.errors.Forbidden:
                    await ctx.send("I do not have permission to join {}".format(ctx.author.voice.channel))
                    return
            else:
                await ctx.send("You must be connected to a voice channel")
                return
        queue = self.get_queue(ctx)
        url = url.strip("<>")
        try:
            song = self.download_video(ctx, url)
        except youtube_dl.utils.DownloadError as error:
            await ctx.send("Failed to download youtube video: {}".format(str(error.exc_info[1]).strip("[youtube] ")))
            return
        except:
            await ctx.send(traceback.format_exc())
            return
        await queue.songs.put(song)
        queue.song_list.append(str(song))
        await ctx.send("Enqueued {}".format(song))
        
    @commands.command()
    async def disconnect(self, ctx):
        """Disconnects the bot from the voice channel"""
        await self.get_queue(ctx).voice_client.disconnect()
        self.clear_data(ctx.guild.id)
        del self.queues[ctx.guild.id]
        await ctx.send("Disconnected")

    @commands.command()
    async def pause(self, ctx):
        """Pauses the current song"""
        self.get_queue(ctx).voice_client.pause()
        await ctx.send("Paused")

    @commands.command()
    async def resume(self, ctx):
        """Resumes playing the current song"""
        self.get_queue(ctx).voice_client.resume()
        await ctx.send("Resumed")

    @commands.command()
    async def skip(self, ctx):
        """Skips a song"""
        queue = self.get_queue(ctx)
        if ctx.author.id in config.dev_ids or ctx.author.id == config.owner_id:
            queue.voice_client.stop()
            await ctx.send("Bot developer skipped the song")
        elif ctx.author == queue.current.requester:
            queue.voice_client.stop()
            await ctx.send("Song requester skipped the song")
        else:
            needed = config.skip_votes_needed
            channel_members = len([member for member in queue.voice_client.channel.members if not member.bot])
            if channel_members <= needed:
                needed = channel_members - 1
            if ctx.author.id not in queue.skip_votes:
                queue.skip_votes.append(ctx.author.id)
            else:
                await ctx.send("You've already voted to skip the song!")
                return
            if len(queue.skip_votes) >= needed:
                queue.voice_client.stop()
                await ctx.send("Song skipped")
            else:
                await ctx.send("Vote added! Currently at {}/{} votes!".format(len(queue.skip_votes), needed))

    @commands.command()
    async def queue(self, ctx):
        """Displays the server's song queue"""
        queue = self.get_queue(ctx)
        if queue.current:
            if not queue.voice_client.is_paused() and not queue.voice_client.is_playing():
                await ctx.send("Nothing is queued")
                return
            else:
                song_list = "Now playing: {}".format(queue.current)
        else:
            await ctx.send("Nothing is queued!")
            return
        if len(queue.song_list) != 0:
            song_list += "\n\n{}".format("\n".join(queue.song_list))
        await ctx.send(song_list)

    @checks.is_dev()
    @commands.command(hidden=True)
    async def volume(self, ctx, amount:float=None):
        """Sets the volume, for developers only because you set the volume via the bot's volume slider. This command is for debugging."""
        queue = self.get_queue(ctx)
        if not amount:
            await ctx.send("The current volume is `{:.0%}`".format(queue.voice_client.source.volume))
            return
        queue.voice_client.source.volume = amount
        await ctx.send("Set the internal volume to `{:.0%}`".format(queue.voice_client.source.volume))

    @commands.command()
    async def np(self, ctx):
        """Shows the song that is currently playing"""
        await ctx.send("Now playing: {} (Requested by {})".format(self.get_queue(ctx).current.title_with_requester))

def setup(bot):
    bot.add_cog(Music(bot))