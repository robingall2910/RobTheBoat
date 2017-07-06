import asyncio
import traceback
import youtube_dl
import os
import subprocess
import shutil

from discord.ext import commands
from utils.tools import *
from utils.mysql import *
from utils.logger import log
from utils.opus_loader import load_opus_lib
from utils import checks

load_opus_lib()

ytdl_format_options = {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3", "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": False, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0", "preferredcodec": "libmp3lame"}

def get_ytdl(id):
    format = ytdl_format_options
    format["outtmpl"] = "data/music/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)

def clear_data(id=None):
    if id is None:
        shutil.rmtree("data/music")
    else:
        shutil.rmtree("data/music/{}".format(id))

class VoiceEntry:
    def __init__(self, message, player, data, file_url):
        self.requester = message.author
        self.channel = message.channel
        self.player = player
        self.data = data
        self.file_url = file_url

    def __str__(self):
        string = "**{}** requested by `{}`".format(self.data["title"], self.requester.display_name)
        duration = self.data["duration"]
        if duration:
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            length = "%02d:%02d:%02d" % (h, m, s)
            string = "{} [`{}`]".format(string, length)
        return string

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.queue = []
        # Set to 0.5 by default to prevent jumpscares
        self.volume = 0.5
        self.skip_votes = set()
        self.audio_player = self.bot.loop.create_task(self.audio_change_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False
        return not self.current.player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_change_task(self):
        while True:
            log.debug("Change task ran")
            if self.current is not None:
                try:
                    os.remove(self.current.file_url)
                except:
                    log.warning("Failed to remove {}".format(self.current.file_url))
            self.play_next_song.clear()
            self.current = await self.songs.get()
            self.queue.remove(self.current)
            await self.bot.send_message(self.current.channel, "Now playing {}".format(self.current))
            self.current.player.volume = self.volume
            self.current.player.start()
            log.debug("\"{}\" is now playing in \"{}\" on \"{}\"".format(self.current.data["title"], self.voice.channel.name, self.current.channel.server.name))
            await self.play_next_song.wait()


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server:discord.Server):
        voice_state = self.voice_states.get(server.id)
        if voice_state is None:
            voice_state = VoiceState(self.bot)
            self.voice_states[server.id] = voice_state
        return voice_state

    async def disconnect_all_voice_clients(self):
        for id in self.voice_states:
            state = self.voice_states[id]
            state.audio_player.cancel()
            await state.voice.disconnect()
        log.debug("All voice clients were disconnected!")

    def clear_cache(self):
        # This is here because I can't call clear_data() from the main class for obvious reasons
        clear_data()

    @commands.command(pass_context=True)
    async def connect(self, ctx):
        """Summons the bot to your current voice channel"""
        if ctx.message.author.voice_channel is None:
            await self.bot.say("You are not in a voice channel")
            return
        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            try:
                state.voice = await self.bot.join_voice_channel(ctx.message.author.voice_channel)
            except:
                await ctx.invoke(self.disconnect)
                await self.bot.say("Something broke. Do {}connect to connect again.".format(self.bot.command_prefix))
                log.debug("Bot failed to connect to voice channel")
                return False
        else:
            await state.voice.move_to(ctx.message.author.voice_channel)
        return True

    @commands.command(pass_context=True)
    async def play(self, ctx, *, song:str):
        """Plays a song, searches youtube or gets video from youtube url"""
        await self.bot.send_typing(ctx.message.channel)
        song = song.strip(str([".play", "<>", "/"]))
        try:
            state = self.get_voice_state(ctx.message.server)
            if state.voice is None:
                success = await ctx.invoke(self.connect)
                if not success:
                    return
            ytdl = get_ytdl(ctx.message.server.id)
            try:
                song_info = ytdl.extract_info(song, download=False, process=False)
                if "url" in song_info:
                    if song_info["url"].startswith("ytsearch"):
                        song_info = ytdl.extract_info(song_info["url"], download=False, process=False)
                        log.debug(song_info)
                    if "entries" in song_info:
                        url = song_info["entries"][0]["url"]
                    else:
                        url = song_info["url"]
                    url = "https://youtube.com/watch?v={}".format(url)
                else:
                    url = song
                log.debug(url)
                song_info = ytdl.extract_info(url, download=True)
                id = song_info["id"]
                title = song_info["title"]
                file_url = "data/music/{}/{}.mp3".format(ctx.message.server.id, id)
                await asyncio.sleep(5)
                player = state.voice.create_ffmpeg_player(file_url, stderr=subprocess.PIPE, after=state.toggle_next)
            except Exception as e:
                await self.bot.say("An error occurred while processing this request: {}".format(py.format("{}: {}\n{}".format(type(e).__name__, e, traceback.format_exc()))))
                return
            player.volume = state.volume
            entry = VoiceEntry(ctx.message, player, song_info, file_url)
            await self.bot.say("Added {} to the queue list!".format(entry))
            await state.songs.put(entry)
            state.queue.append(entry)
        except Exception as e:
            await self.bot.say(traceback.format_exc())
            log.debug("{}: {}\n\n{}".format(type(e).__name__, e, traceback.format_exc()))

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, amount:int):
        """Sets the volume"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = amount / 100
            state.volume = amount / 100
            await self.bot.say("Okay, I set the volume to `{:.0%}`.".format(player.volume))
        else:
            await self.bot.say("I forgot, but uh, nothing's playing man.")

    @commands.command(pass_context=True)
    async def disconnect(self, ctx):
        """Disconnects the bot from the voice channel"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.stop()
        try:
            state.audio_player.cancel()
            del self.voice_states[ctx.message.server.id]
            await state.voice.disconnect()
        except:
            log.debug("Bot failed to disconnect from voice channel, forcing disconnection...")
            if ctx.message.server.me.voice_channel:
                try:
                    await ctx.message.server.voice_client.disconnect()
                except:
                    log.error("Bot failed to force the disconnection from a voice channel!\n{}".format(traceback.format_exc()))
                    pass
        await self.bot.say("Alright, I left the voice channel.")

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        """Vote to skip a song. Server mods, the server owner, bot developers, and the song requester can skip the song"""
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say("Nothing's playing, once again.")
            return
        voter = ctx.message.author
        mod_role_name = read_data_entry(ctx.message.server.id, "mod-role")
        mod = discord.utils.get(voter.roles, name=mod_role_name)
        if voter == state.current.requester:
            await self.bot.say("The requester chose to skip the song.")
            state.skip()
        elif mod:
            await self.bot.say("Server moderator didn't like the song, skipping it.")
            state.skip()
        elif voter == ctx.message.server.owner:
            await self.bot.say("Server owner hates the song. Skipping it.")
            state.skip()
        elif checks.is_dev_check(ctx.message.author):
            await self.bot.say("Bot developer doesn't love you. Skipping song...")
            state.skip()
        elif voter.id not in state.skip_votes:
            votes_needed = 3
            members = []
            for member in state.voice.channel.voice_members:
                if not member.bot:
                    members.append(member)
            if len(members) < 3:
                votes_needed = len(members)
            if not state.voice.channel.voice_members:
                await bot.say("You aren't in the voice channel. Please connect and you'll be able to skip the song.")
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= votes_needed:
                await self.bot.say("All of the required votes were passed on, skipping the song.")
                state.skip()
            else:
                await self.bot.say("Added the skip vote. Currently at `{}/{}`".format(total_votes, votes_needed))
        else:
            await self.bot.say("You already voted it, I know you hate it, but wait.")

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        """Pauses the player"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
            await self.bot.say("Alright, pausing the song.")
        else:
            await self.bot.say("Hey, I can't pause dead air!")

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        """Resumes the player"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
            await self.bot.say("Welcome back! Resuming the song.")
        else:
            await self.bot.say("What, are you expecting me to resume nothing?")

    @commands.command(pass_context=True)
    async def queue(self, ctx):
        """Displays the song queue"""
        state = self.get_voice_state(ctx.message.server)
        songs = state.queue
        if len(songs) == 0 and not state.current:
            await self.bot.say("Queue is empty, my boy.")
        else:
            current_song = "Raping your ears with: {}".format(state.current)
            if len(songs) != 0:
                songs = "{}\n\n{}".format(current_song, "\n".join([str(song) for song in songs]))
            else:
                songs = "{}".format(current_song)
            await self.bot.say(songs)

    @commands.command(hidden=True, pass_context=True)
    @checks.is_dev()
    async def musicdebug(self, ctx, *, shit:str):
        """This is the part where I make 20,000 typos before I get it right"""
        # "what the fuck is with your variable naming" - EJH2
        try:
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            await self.bot.say(py.format(rebug))
        except Exception as damnit:
            await self.bot.say(py.format("{}: {}".format(type(damnit).__name__, damnit)))

def setup(bot):
    bot.add_cog(Music(bot))