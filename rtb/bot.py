import os
import sys
import time
import shlex
import shutil
import inspect
import discord
import asyncio
import traceback
import gspread
import json
import io
import cleverbot
import re
import random
import aiohttp
import platform
import wikipedia
import wikipedia.exceptions
import datetime
import copy

from oauth2client.service_account import ServiceAccountCredentials
from gspread import exceptions

from discord import utils
from discord.object import Object
from discord.enums import ChannelType
from discord.voice_client import VoiceClient

from io import BytesIO
from functools import wraps
from textwrap import dedent
from datetime import timedelta
from random import choice, shuffle
from collections import defaultdict
from subprocess import call
from subprocess import check_output

from rtb.playlist import Playlist
from rtb.player import MusicPlayer
from rtb.config import Config, ConfigDefaults, ChallongeConfig
from rtb.permissions import Permissions, PermissionsDefaults
from rtb.playlist import Playlist
from rtb.utils import load_file, write_file, sane_round_int, extract_user_id
from rtb.credentials import app_id

from . import exceptions
from . import downloader
from .opus_loader import load_opus_lib
from .constants import VERSION as BOTVERSION
from .constants import DISCORD_MSG_CHAR_LIMIT, AUDIO_CACHE_PATH
from .constants import VER
from .constants import BDATE as BUILD
from .constants import MAINVER as MVER
from .constants import BUILD_USERNAME as BUNAME
from _operator import contains

load_opus_lib()
st = time.time()
# xl color formatting
xl = "```xl\n{0}\n```"

dis_games = [
    discord.Game(name='with fire'),
    discord.Game(name='with Robin'),
    discord.Game(name='baa'),
    discord.Game(name='Denzel Curry - Ultimate'),
    discord.Game(name='Windows XP'),
    discord.Game(name='Drake - Jumpman'),
    discord.Game(name='with Kyle'),
    discord.Game(name='Super Smash Bros. Melee'),
    discord.Game(name='.help for help!'),
    discord.Game(name='how to lose a phone'),
    discord.Game(name='with memes'),
    discord.Game(name='Sergal'),
    discord.Game(name='Fox'),
    discord.Game(name='Dragon'),
    discord.Game(name='with some floof'),
    discord.Game(name='with Napstabot'),
    discord.Game(name='DramaNation'),
    discord.Game(name='browsing 4chan'),
    discord.Game(name="Guns N' Roses"),
    discord.Game(name='vaporwave'),
    discord.Game(name='being weird'),
    discord.Game(name='stalking Twitter'),
    discord.Game(name='Microsoft Messaging'),
    discord.Game(name="out in the club and I'm sippin' that bubb"),
    discord.Game(name="Let's get riiiiiiight into the news!"),
    discord.Game(name='Twenty One Pilots'),
    discord.Game(name='Twenty Juan Pilots'),
    discord.Game(name="I've gone batty!"),
    discord.Game(name='Lunatic under the moon'),
    discord.Game(name='with the idea of democratic socialism'),
    discord.Game(name='with the idea of a totalitarian dictatorship'),
    discord.Game(name="with Donald Trump's hair"),
    discord.Game(name='Quake'),
    discord.Game(name='Quake II'),
    discord.Game(name='Quake III Arena'),
    discord.Game(name='Here in my garage, just bought this, uh, new Lamborghini here.'),
    discord.Game(name='Cyka-Strike: Blyat Offensive'),
    discord.Game(name='the NSA for fools'),
    discord.Game(name='3.14159265358979323846264338327950288'),
    discord.Game(name="No more charades, my heart's been displayed"),
    discord.Game(name='I have a suggestion.'),
    discord.Game(name="If you're reading this, it's too late."),
    discord.Game(name='all the girls in the club'),
    discord.Game(name='all the guys in the club'),
    discord.Game(name='Never trust me with your secrets.'),
    discord.Game(name='Hey, you! I... I... I have a crush on you.'),
    discord.Game(name='Yandere Simulator'),
    discord.Game(name='VACation Simulator'),
    discord.Game(name='#BotLivesMatter'),
    discord.Game(name='with my DS'),
    discord.Game(name='learning Greek'),
    discord.Game(name='learning Japanese'),
    discord.Game(name='learning Swedish'),
    discord.Game(name='learning Spanish'),
    discord.Game(name='BLAME CANADA!'),
    discord.Game(name='Did you expect something witty and clever?'),
    discord.Game(name='hockey'),
    discord.Game(name='football'),
    discord.Game(name='basketball'),
    discord.Game(name='lacrosse'),
    discord.Game(name='baseball'),
    discord.Game(name='golf'),
    discord.Game(name='XDXDXDXDXDXDXD'),
    discord.Game(name='the game of nil.'),
    discord.Game(name='there are many knots i cannot untie.'),
    discord.Game(name='through the ceiling.'),
    discord.Game(name='(null)'),
    discord.Game(name='with my tiddy'),
    discord.Game(name='i have 9 bandaids on my penis'),
    discord.Game(name='explorer.exe'),
    discord.Game(name='tinder'),
    discord.Game(name='Minion Pregnancy flash game'),
    discord.Game(name='discord.Game(name="penis")'),
    discord.Game(name='tuna'),
    discord.Game(name='SUPER'),
    discord.Game(name='HOT'),
    discord.Game(name='I PLEDGE ALLEGIANCE, TO THE FLAG, OF THE UNITED STATES OF AMERICA.'),
    discord.Game(name='Capitalism is on its way out.'),
    discord.Game(name='THE SINGULARITY'),
    discord.Game(name='6.0221409e+23'),
    discord.Game(name='68'),
    discord.Game(name='ALT+F4'),
    discord.Game(name='Minecraft 2.0 baby XDXD'),
    discord.Game(name='where do babies come from?'),
    discord.Game(name='my uteri is expanding'),
    discord.Game(name='your mom XDDDDDDDDDDDD'),
    discord.Game(name='I am not a contributing member of society.'),
    discord.Game(name='Meincraft'),
    discord.Game(name='i dont know a lot of python.'),
    discord.Game(name='WILL'),
    discord.Game(name='ROBIN'),
    discord.Game(name='DREW'),
    discord.Game(name='ITS THE LAW.'),
    discord.Game(name='DOOM'),
    discord.Game(name='Fallout Shelter is now available for PC! Install it now.'),
    discord.Game(name='9:30 PM'),
    discord.Game(name='why would anyone think that this is my golden ticket idea?'),
    discord.Game(name='PRESSURE, PRESSURE, NOOSE AROUND MY NECK'),
    discord.Game(name='jenna is cute'),
    discord.Game(name='crippling social anxiety'),
    discord.Game(name='HMU ON YOUTUBE: http://youtube.com/c/FUCKBOIS2016'),
    discord.Game(name='Ow, my head hurts.')
]

# Regex for IP address
ipv4_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
ipv6_regex = re.compile(
    r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))')

ratelevel = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10"
]

tweetsthatareokhand = [
    "http://i.imgur.com/lkMJ1O9.png",
    "http://i.imgur.com/rbGmZqV.png",
    "http://i.imgur.com/hYzNxVR.png",
    "http://i.imgur.com/JuVsIMg.png",
    "http://i.imgur.com/2NYwUcj.png",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222734961442817/uh_semen.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222732260442113/train_of_horses.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222728338636802/they_wshiper.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222725977243650/thats_my_boyfriend.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222723175579650/pinned.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222720667385858/list.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222717743824907/idea_of_music.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222715147550721/goals.PNG",
    "https://cdn.discordapp.com/attachments/173887966031118336/177222711867604993/disturbing_fetish.PNG",
    #    "here's a message from the coder of this: I FUCKING RAN OUT NEEDS MORE CHEESE",
    # not anymore, its like what 21 links
    "​https://cdn.discordapp.com/attachments/173886531080159234/176425292426903553/f20e683862a17ef49633eed742fc2b22eb17220eef5a1d607cda2e7a7758720b_1.jpg",
    "http://i.imgur.com/m71nJAg.png",
    "http://i.imgur.com/m5fx7U9.png",
    "https://cdn.discordapp.com/attachments/173887966031118336/177518766781890562/your-resistance-only-makes-my-penis-harder.jpg",
    "http://i.imgur.com/21bV05w.png",
    "http://i.imgur.com/7Y94F7L.png"
]

suicidalmemes = [
    "what the hell did you do idiot",
    "wtf ok idiot fool",
    "you killed him nice job.",
    "lmao you killed him gg on your killing :ok_hand:",
    "party on his death? lit",
    "fuckin fag wtf no.... y..."
]

throwaf = [
    "a keyboard",
    "a Playstation 4",
    "a PSP with Crash Bandicoot 2 on it",
    "a fur coat",
    "furtrash called art",
    "a british trash can",
    "a raincoat made with :heart:",
    "some shitty pencil, it's definitely useless",
    "a dragon",
    "a Lightning Dragon",
    "Mαxie",
    "Robin",
    "a water bucket",
    "water",
    "a shamrock shake",
    "flowers",
    "some fisting",
    "a RoboNitori message",
    "a ice cream cone",
    "hot ass pie, and it's strawberry",
    "a strawberry ice cream cone",
    "Visual Studio 2015",
    "Toshiba Satellite laptop with Spotify, Guild Wars 2 and Visual Studio on it",
    "a compass",
    "honk honk",
    "pomfpomfpomf",
    "⑨",
    "a watermelone",
    "FUCKING PAPERCLIP",
    "HTTP Error 403",
    "Error 429",
    "`never`",
    "`an error that should be regretted of`",
    "Georgia",
    "New York",
    "Nevada",
    "Michigan",
    "Florida",
    "California",
    "TEEEEEEXASSSSSSS",
    "a climaxing dragon picture"
    "Nebraska",
    "an ok ok please message",
    "a pleb called EJH2",
    "15 dust bunnies, a water bottle, and a iron hammer to ban people with",
    "a broken glass (dance bitch)",
    "ok ok",
    "allergy pills",
    "a Chocolate Calculator",
    "probably not Bad Dragon toy",
    "aww yiss a piece of WORLD DOMINATION POWER",
    "a prime minister from Canada",
    "Indiana",
    "a coca-cola bottle",
    "a DJ System",
    "a fridge with wifi enabled",
    "a router",
    "a modem box",
    "a Napstabot",
    "another RoboNitori sentence",
    "a phone",
    "a fan",
    "a pair of earphones",
    "Excel document",
    "Paint Tool SAI painting",
    "Word Document",
    "Visual Studio Project",
    "nerd thing",
    "python 3.5 py",
    "fuckin office tool",
    "clippy",
    "dat boi meme",
    "random.jpeg",
    "Danny DeVito",
    "Deadpool",
    "a Lenovo Keyboard",
    "Life of Pablo",
    "a Mexican called Ambrosio",
    "the most obvious dick master",
    "Motopuffs",
    "Motopuffs",
    "the dick master called Motopuffs",
    "a weeaboo",
    "Ryulise, the stupid smash master",
    "death, at its finest",
    "morth, but not in its final form",
    "some flaccid sword"
]


class Lmgtfy:
    def __init__(self):
        # nothing
        self.name = 'Lmgtfy'

    def lmgtfy_url(self, query):
        print('query in lmgtfy: ' + str(query))
        newQuery = query.replace(' ', "+")
        print('newQuery in lmgtfy: ' + str(newQuery))
        return 'http://lmgtfy.com/?q=' + str(''.join([word.replace(" ", "+") for word in query.strip()]))
        # return 'http://lmgtfy.com/?q=' + '+'.join([word.strip().replace(" ", "+") for word in query.strip()])

    def short_url(self, query):
        print('query in lmgtfy: ' + str(query))
        payload = {'format': 'json', 'url': self.lmgtfy_url(query)}
        r = requests.get('http://is.gd/create.php', params=payload)
        print('response shortlink: ' + str(r.json()['shorturl']))
        return r.json()['shorturl']

class PlatformSpecs:
    def __init__(self):
        self.platformObj = platform
        self.machine = platform.machine()
        self.version = platform.version()
        self.platform = platform.platform()
        self.uname = platform.uname()
        self.system = platform.system()
        self.processor = platform.processor()

    def getPlatObj(self):
        return self.platformObj

    def getMachine(self):
        return self.machine

    def getVersion(self):
        return self.version

    def getPlatform(self):
        return self.platform

    def getPlatUName(self):
        return self.uname

    def getSys(self):
        return self.system

    def getProcessor(self):
        return self.processor

class SkipState:
    def __init__(self):
        self.skippers = set()
        self.skip_msgs = set()

    @property
    def skip_count(self):
        return len(self.skippers)

    def reset(self):
        self.skippers.clear()
        self.skip_msgs.clear()

    def add_skipper(self, skipper, msg):
        self.skippers.add(skipper)
        self.skip_msgs.add(msg)
        return self.skip_count


class Response:
    def __init__(self, content, reply=False, delete_after=0):
        self.content = content
        self.reply = reply
        self.delete_after = delete_after


class RTB(discord.Client):
    def __init__(self, config_file=ConfigDefaults.options_file, perms_file=PermissionsDefaults.perms_file,
                 excel_file=ConfigDefaults.excel_file, challonge_file=ConfigDefaults.challonge_file,
                 saying_file=ConfigDefaults.saying_file):
        super().__init__()

        self.players = {}
        self.the_voice_clients = {}
        self.voice_client_connect_lock = asyncio.Lock()
        self.voice_client_move_lock = asyncio.Lock()
        self.aiosession = aiohttp.ClientSession(loop=self.loop)

        self.config = Config(config_file)
        self.permissions = Permissions(perms_file, grant_all=[self.config.owner_id])

        self.blacklist = set(load_file(self.config.blacklist_file))
        self.whitelist = set(load_file(self.config.whitelist_file))
        self.autoplaylist = load_file(self.config.auto_playlist_file)
        self.downloader = downloader.Downloader(download_folder='audio_cache')
        self.uptime = datetime.datetime.utcnow()
        # self.voice_clients = {}
        # self.voice_client_connect_lock = asyncio.Lock()
        self.config = Config(config_file)
        self.challongeconfig = ChallongeConfig(challonge_file)
        self.excel_file = excel_file
        self.permissions = Permissions(perms_file)
        self.lock_checkin = False
        self.lmgtfy = Lmgtfy()
        self.platform = PlatformSpecs()
        self.checkinActive = False  # bool to handle checkin loop

        self.exit_signal = None

        if not self.autoplaylist:
            print("Warning: Autoplaylist is empty, disabling.")
            self.config.auto_playlist = False

        # self.headers['user-agent'] += ' RobTheBoat Discord/%s' % BOTVERSION # Now it's reverse.
        self.http.user_agent += ' RobTheBoat Discord/%s' % BOTVERSION
        # ^ for somewhat reason

        # TODO: Fix these
        # These aren't multi-server compatible, which is ok for now, but will have to be redone when multi-server is possible
        ssd_defaults = {'last_np_msg': None, 'auto_paused': False}
        self.server_specific_data = defaultdict(lambda: dict(ssd_defaults))

    # TODO: Add some sort of `denied` argument for a message to send when someone else tries to use it
    def owner_only(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Only allow the owner to use these commands
            orig_msg = self._get_variable('message')

            if not orig_msg or orig_msg.author.id == self.config.owner_id:
                return await func(self, *args, **kwargs)
            else:
                raise exceptions.PermissionsError("only the owner can use this command", expire_in=30)

        return wrapper

    @staticmethod
    def _fixg(x, dp=2):
        return ('{:.%sf}' % dp).format(x).rstrip('0').rstrip('.')

    def _get_variable(self, name):
        stack = inspect.stack()
        try:
            for frames in stack:
                current_locals = frames[0].f_locals
                if name in current_locals:
                    return current_locals[name]
        finally:
            del stack

    def _get_owner(self, voice=False):
        if voice:
            for server in self.servers:
                for channel in server.channels:
                    for m in channel.voice_members:
                        if m.id == self.config.owner_id:
                            return m
        else:
            return discord.utils.find(lambda m: m.id == self.config.owner_id, self.get_all_members())

    def _delete_old_audiocache(self, path=AUDIO_CACHE_PATH):
        try:
            shutil.rmtree(path)
            return True
        except:
            try:
                os.rename(path, path + '__')
            except:
                return False
            try:
                shutil.rmtree(path)
            except:
                os.rename(path + '__', path)
                return False

        return True

    async def log(self, string, channel=None):
        """
            Logs information to a Discord text channel
            :param channel: - The channel the information originates from
        """
        if channel:
            if self.config.log_subchannels:
                for i in set(self.config.log_subchannels):
                    subchannel = self.get_channel(i)
                    if not subchannel:
                        self.config.log_subchannels.remove(i)
                        print("[Warning] Bot can't find logging subchannel: {}".format(i))
                    else:
                        server = subchannel.server
                        if channel in server.channels:
                            await self.safe_send_message(subchannel, ":stopwatch: `{}` ".format(
                                time.strftime(self.config.log_timeformat)) + string)

            if self.config.log_masterchannel:
                id = self.config.log_masterchannel
                master = self.get_channel(id)
                if not master:
                    self.config.log_masterchannel = None
                    print("[Warning] Bot can't find logging master channel: {}".format(id))
                else:
                    await self.safe_send_message(master, ":stopwatch: `{}` :mouse_three_button: `{}` ".format(
                        time.strftime(self.config.log_timeformat), channel.server.name) + string)

        else:
            if self.config.log_masterchannel:
                id = self.config.log_masterchannel
                master = self.get_channel(id)
                if not master:
                    self.config.log_masterchannel = None
                    print("[Warning] Bot can't find logging master channel: {}".format(id))
                else:
                    await self.safe_send_message(master, ":stopwatch: `{}` ".format(
                        time.strftime(self.config.log_timeformat)) + string)

    # TODO: autosummon option to a specific channel
    async def _auto_summon(self, channel=None):
        owner = self._get_owner(voice=True)
        if owner:
            self.safe_print("Found owner in voice channel \"%s\", attempting to join..." % owner.voice_channel.name)
            # TODO: Effort
            await self.cmd_summon(owner.voice_channel, owner, None)
            return owner.voice_channel

    async def _autojoin_channels(self):
        joined_servers = []

        for chid in self.config.autojoin_channels:
            channel = self.get_channel(chid)
            if channel.server in joined_servers:
                print("Already joined a channel in %s, skipping" % channel.server.name)
                continue

            if channel and channel.type == discord.ChannelType.voice:
                self.safe_print("Attempting to autojoin %s in %s" % (channel.name, channel.server.name))

                chperms = channel.permissions_for(channel.server.me)

                if not chperms.connect:
                    self.safe_print("No perms to join \"%s\"." % channel.name)
                    continue

                elif not chperms.speak:
                    self.safe_print("Unable to join \"%s\", can't speak." % channel.name)
                    continue

                try:
                    player = await self.get_player(channel, create=True)

                    if player.is_stopped:
                        player.play()

                    if self.config.auto_playlist:
                        await self.on_finished_playing(player)

                    joined_servers.append(channel.server)
                except Exception as e:
                    if self.config.log_exceptions:
                        await self.log(
                            ":warning: Could not join %s\n```python\n%s\n```" % (channel.name, traceback.print_exc()),
                            channel)
                    print("Failed to join", channel.name)
            elif channel:
                if self.config.log_exceptions:
                    await self.log(":warning: Could not join %s because it is a text channel" % channel.name, channel)
                print("Not joining %s on %s, that's a text channel." % (channel.name, channel.server.name))

            else:
                print("Invalid channel id: " + chid)

    async def _wait_delete_msg(self, message, after):
        await asyncio.sleep(after)
        await self.safe_delete_message(message)

    # TODO: Check to see if I can just move this to on_message after the response check
    async def _manual_delete_check(self, message, *, quiet=False):
        if self.config.delete_invoking:
            await self.safe_delete_message(message, quiet=quiet)

    async def _check_ignore_non_voice(self, msg):
        vc = msg.server.me.voice_channel

        # If we've connected to a voice chat and we're in the same voice channel
        if not vc or vc == msg.author.voice_channel:
            return True
        else:
            raise exceptions.PermissionsError(
                "you cannot use this command when not in the voice channel (%s)" % vc.name, expire_in=30)

    async def get_voice_client(self, channel):
        if isinstance(channel, Object):
            channel = self.get_channel(channel.id)

        if getattr(channel, 'type', ChannelType.text) != ChannelType.voice:
            raise AttributeError('Channel passed must be a voice channel')

        with await self.voice_client_connect_lock:
            server = channel.server
            if server.id in self.the_voice_clients:
                return self.the_voice_clients[server.id]

            s_id = self.ws.wait_for('VOICE_STATE_UPDATE', lambda d: d.get('user_id') == self.user.id)
            _voice_data = self.ws.wait_for('VOICE_SERVER_UPDATE', lambda d: True)

            await self.ws.voice_state(server.id, channel.id)

            s_id_data = await asyncio.wait_for(s_id, timeout=10, loop=self.loop)
            voice_data = await asyncio.wait_for(_voice_data, timeout=10, loop=self.loop)
            session_id = s_id_data.get('session_id')

            kwargs = {
                'user': self.user,
                'channel': channel,
                'data': voice_data,
                'loop': self.loop,
                'session_id': session_id,
                'main_ws': self.ws
            }
            voice_client = VoiceClient(**kwargs)
            self.the_voice_clients[server.id] = voice_client

            retries = 3
            for x in range(retries):
                try:
                    await self.log(":mega: Attempting connection: `%s`" % server.name)
                    print("Attempting connection...")
                    await asyncio.wait_for(voice_client.connect(), timeout=10, loop=self.loop)
                    await self.log(":mega: Connected to: `%s`" % server.name)
                    print("Connection established.")
                    break
                except:
                    print("Failed to connect, retrying (%s/%s)..." % (x + 1, retries))
                    await asyncio.sleep(1)
                    await self.ws.voice_state(server.id, None, self_mute=True)
                    await asyncio.sleep(1)

                    if x == retries - 1:
                        await self.log(":warning: `%s`: Failed to connect" % server.name)
                        raise exceptions.HelpfulError(
                            "Cannot establish connection to voice chat.  "
                            "Something may be blocking outgoing UDP connections.",

                            "This may be an issue with a firewall blocking UDP.  "
                            "Figure out what is blocking UDP and disable it.  "
                            "It's most likely a system firewall or overbearing anti-virus firewall.  "
                        )

            return voice_client

    async def mute_voice_client(self, channel, mute):
        await self._update_voice_state(channel, mute=mute)

    async def deafen_voice_client(self, channel, deaf):
        await self._update_voice_state(channel, deaf=deaf)

    async def move_voice_client(self, channel):
        await self._update_voice_state(channel)

    async def disconnect_voice_client(self, server):
        if server.id not in self.the_voice_clients:
            return

        if server.id in self.players:
            self.players.pop(server.id).kill()

        await self.the_voice_clients.pop(server.id).disconnect()

    async def disconnect_all_voice_clients(self):
        for vc in self.the_voice_clients.copy():
            await self.disconnect_voice_client(self.the_voice_clients[vc].channel.server)

    async def _update_voice_state(self, channel, *, mute=False, deaf=False):
        if isinstance(channel, Object):
            channel = self.get_channel(channel.id)

        if getattr(channel, 'type', ChannelType.text) != ChannelType.voice:
            raise AttributeError('Channel passed must be a voice channel')

        # I'm not sure if this lock is actually needed
        with await self.voice_client_move_lock:
            server = channel.server

            payload = {
                'op': 4,
                'd': {
                    'guild_id': server.id,
                    'channel_id': channel.id,
                    'self_mute': mute,
                    'self_deaf': deaf
                }
            }

            await self.ws.send(utils.to_json(payload))
            self.the_voice_clients[server.id].channel = channel

    async def get_player(self, channel, create=False):
        server = channel.server

        if server.id not in self.players:
            if not create:
                raise exceptions.CommandError(
                    'The bot is not in a voice channel.  '
                    'Use %ssummon to summon it to your voice channel.' % self.config.command_prefix)

            voice_client = await self.get_voice_client(channel)

            playlist = Playlist(self)
            player = MusicPlayer(self, voice_client, playlist) \
                .on('play', self.on_play) \
                .on('resume', self.on_resume) \
                .on('pause', self.on_pause) \
                .on('stop', self.on_stop) \
                .on('finished-playing', self.on_finished_playing) \
                .on('entry-added', self.on_entry_added)

            player.skip_state = SkipState()
            self.players[server.id] = player

        return self.players[server.id]

    async def on_play(self, player, entry):
        await self.update_now_playing(entry)
        player.skip_state.reset()

        channel = entry.meta.get('channel', None)
        author = entry.meta.get('author', None)

        if channel and author:
            last_np_msg = self.server_specific_data[channel.server]['last_np_msg']
            if last_np_msg and last_np_msg.channel == channel:

                async for lmsg in self.logs_from(channel, limit=1):
                    if lmsg != last_np_msg and last_np_msg:
                        await self.safe_delete_message(last_np_msg)
                    if self.config.log_interaction:
                        await self.log(":microphone: `%s` (requested by `%s`) is now playing in **%s**" % (
                        entry.title, entry.meta['author'], player.voice_client.channel.name), channel)

                        self.server_specific_data[channel.server]['last_np_msg'] = None
                    break  # This is probably redundant

            if self.config.now_playing_mentions:
                newmsg = '%s - your song **%s** is now playing in %s!' % (
                    entry.meta['author'].mention, entry.title, player.voice_client.channel.name)
            else:
                newmsg = 'Now playing in %s: **%s**' % (
                    player.voice_client.channel.name, entry.title)

            if self.server_specific_data[channel.server]['last_np_msg']:
                self.server_specific_data[channel.server]['last_np_msg'] = await self.safe_edit_message(last_np_msg,
                                                                                                        newmsg,
                                                                                                        send_if_fail=True)
            else:
                self.server_specific_data[channel.server]['last_np_msg'] = await self.safe_send_message(channel, newmsg)

    async def on_resume(self, entry, **_):
        await self.update_now_playing(entry)

    async def on_pause(self, entry, **_):
        await self.update_now_playing(entry, True)

    async def on_stop(self, **_):
        await self.update_now_playing()

    async def on_finished_playing(self, player, **_):
        if not player.playlist.entries and not player.current_entry and self.config.auto_playlist:
            while self.autoplaylist:
                song_url = choice(self.autoplaylist)
                info = await self.downloader.safe_extract_info(player.playlist.loop, song_url, download=False,
                                                               process=False)

                if not info:
                    self.autoplaylist.remove(song_url)
                    self.safe_print("[Info] Removing unplayable song from autoplaylist: %s" % song_url)
                    write_file(self.config.auto_playlist_file, self.autoplaylist)
                    continue

                if info.get('entries', None):  # or .get('_type', '') == 'playlist'
                    pass  # Wooo playlist
                    # Blarg how do I want to do this

                # TODO: better checks here
                try:
                    await player.playlist.add_entry(song_url, channel=None, author=None)
                except exceptions.ExtractionError as e:
                    print("Error adding song from autoplaylist:", e)
                    continue

                break

            if not self.autoplaylist:
                print("[Warning] No playable songs in the autoplaylist, disabling.")
                self.config.auto_playlist = False

    async def on_entry_added(self, playlist, entry, **_):
        pass

    async def update_now_playing(self, entry=None, is_paused=False):
        game = None

        if self.user.bot:
            activeplayers = sum(1 for p in self.players.values() if p.is_playing)
            if activeplayers > 1:
                # game = discord.Game(name=".donate and .updates - on %s voice channels" % activeplayers)
                game = random.choice(dis_games)
                entry = None

            elif activeplayers == 1:
                player = discord.utils.get(self.players.values(), is_playing=True)
                entry = player.current_entry

        if entry:
            prefix = u'\u275A\u275A ' if is_paused else ''

            name = u'{}{}'.format(prefix, entry.title)[:128]
            game = random.choice(dis_games)
            randomize = [
                self.change_status(game, idle=False),
                self.change_status(game, idle=True),
                self.change_status(game, idle=False),
                self.change_status(game, idle=True)
            ]

        await random.choice(randomize)

    async def safe_send_message(self, dest, content, *, tts=False, expire_in=0, also_delete=None, quiet=False):
        msg = None
        try:
            msg = await self.send_message(dest, content, tts=tts)

            if msg and expire_in:
                asyncio.ensure_future(self._wait_delete_msg(msg, expire_in))

            if also_delete and isinstance(also_delete, discord.Message):
                asyncio.ensure_future(self._wait_delete_msg(also_delete, expire_in))

        except discord.Forbidden:
            if not quiet:
                self.safe_print("Warning: Cannot send message to %s, no permission" % dest.name)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot send message to %s, invalid channel?" % dest.name)

        return msg

    async def safe_delete_message(self, message, *, quiet=False):
        try:
            return await self.delete_message(message)

        except discord.Forbidden:
            if not quiet:
                self.safe_print("Warning: Cannot delete message \"%s\", no permission" % message.clean_content)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot delete message \"%s\", message not found" % message.clean_content)

    async def safe_edit_message(self, message, new, *, send_if_fail=False, quiet=False):
        try:
            return await self.edit_message(message, new)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot edit message \"%s\", message not found" % message.clean_content)
            if send_if_fail:
                if not quiet:
                    print("Sending instead")
                return await self.safe_send_message(message.channel, new)

    def safe_print(self, content, *, end='\n', flush=True):
        sys.stdout.buffer.write((content + end).encode('utf-8', 'replace'))
        if flush: sys.stdout.flush()

    async def send_typing(self, destination):
        try:
            return await super().send_typing(destination)
        except discord.Forbidden:
            if self.config.debug_mode:
                print("Could not send typing to %s, no permssion" % destination)

    def _cleanup(self):
        try:
            self.loop.run_until_complete(self.logout())
        except:  # Can be ignored
            pass

        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)

        try:
            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except:  # Can be ignored
            pass

    # noinspection PyMethodOverriding
    def run(self):
        try:
            self.loop.run_until_complete(self.start(*self.config.auth))

        except discord.errors.LoginFailure:
            # Add if token, else
            raise exceptions.HelpfulError(
                "Bot cannot login, bad credentials.",
                "Fix your Email or Password or Token in the options file.  "
                "Remember that each field should be on their own line.")

        finally:
            try:
                self._cleanup()
            except Exception as e:
                print("Error in cleanup:", e)

            self.loop.close()
            if self.exit_signal:
                raise self.exit_signal

    async def logout(self):
        for vc in self.the_voice_clients.values():
            try:
                await vc.disconnect()
            except:
                continue

        return await super().logout()

    async def on_error(self, event, *args, **kwargs):
        ex_type, ex, stack = sys.exc_info()

        if ex_type == exceptions.HelpfulError:
            print("Exception in", event)
            print(ex.message)

            await asyncio.sleep(2)  # don't ask
            await self.logout()

        elif issubclass(ex_type, exceptions.Signal):
            self.exit_signal = ex_type
            await self.logout()

        else:
            traceback.print_exc()

    async def on_ready(self):
        print('---------------------------------------')
        print('\rConnected!  RTB System v%s\n' % BOTVERSION)

        if self.config.owner_id == self.user.id:
            raise exceptions.HelpfulError(
                "Your OwnerID is incorrect or you've used the wrong credentials.",

                "The bot needs its own account to function.  "
                "The OwnerID is the id of the owner, not the bot.  "
                "Figure out which one is which and use the correct information.")

        self.safe_print("Bot:   %s/%s#%s" % (self.user.id, self.user.name, self.user.discriminator))

        owner = self._get_owner(voice=True) or self._get_owner()
        if owner and self.servers:
            self.safe_print("Owner: %s/%s#%s\n" % (owner.id, owner.name, owner.discriminator))

            print('Server List:')
            [self.safe_print(' - ' + s.name) for s in self.servers]

        elif self.servers:
            print("Owner could not be found on any server (id: %s)\n" % self.config.owner_id)

            print('Server List:')
            [self.safe_print(' - ' + s.name + ' - ' + str(s.id)) for s in self.servers]

        else:
            print("Owner unavailable, bot is not on any servers.")
            # if bot: post help link, else post something about invite links

        print()

        if self.config.log_masterchannel:
            print("Logging to master channel:")
            channel = self.get_channel(self.config.log_masterchannel)
            if channel:
                self.safe_print(' - %s/%s' % (channel.server.name.strip(), channel.name.strip()))
        if self.config.log_subchannels:
            print("Logging to subchannels:")
            chlist = [self.get_channel(i) for i in self.config.log_subchannels if i]
            [self.safe_print(' - %s/%s' % (ch.server.name.strip(), ch.name.strip())) for ch in chlist if ch]
        if self.config.log_masterchannel or self.config.log_subchannels:
            print("  Exceptions: " + ['Disabled', 'Enabled'][self.config.log_exceptions])
            print("  Interaction: " + ['Disabled', 'Enabled'][self.config.log_interaction])
            print("  Downloads: " + ['Disabled', 'Enabled'][self.config.log_downloads])
            print("  Time Format: {}".format(self.config.log_timeformat))
        else:
            print("Not logging to any text channels")

        print()

        if self.config.bound_channels:
            print("Bound to text channels:")
            chlist = [self.get_channel(i) for i in self.config.bound_channels if i]
            [self.safe_print(' - %s/%s' % (ch.server.name.strip(), ch.name.strip())) for ch in chlist if ch]
        else:
            print("Not bound to any text channels")

        print()
        print("Options:")

        self.safe_print("  Command prefix: " + self.config.command_prefix)
        print("  Default volume: %s%%" % int(self.config.default_volume * 100))
        print("  Skip threshold: %s votes or %s%%" % (
            self.config.skips_required, self._fixg(self.config.skip_ratio_required * 100)))
        print("  Whitelist: " + ['Disabled', 'Enabled'][self.config.white_list_check])
        print("  Now Playing @mentions: " + ['Disabled', 'Enabled'][self.config.now_playing_mentions])
        print("  Auto-Summon: " + ['Disabled', 'Enabled'][self.config.auto_summon])
        print("  Auto-Playlist: " + ['Disabled', 'Enabled'][self.config.auto_playlist])
        print("  Auto-Pause: " + ['Disabled', 'Enabled'][self.config.auto_pause])
        print("  Delete Messages: " + ['Disabled', 'Enabled'][self.config.delete_messages])
        if self.config.delete_messages:
            print("  Delete Invoking: " + ['Disabled', 'Enabled'][self.config.delete_invoking])
        print("  Downloaded songs will be %s" % ['deleted', 'saved'][self.config.save_videos])
        print()

        # maybe option to leave the ownerid blank and generate a random command for the owner to use
        # wait_for_message is pretty neato

        await self.log(":mega: `{}#{}` ready".format(self.user.name, self.user.discriminator, time.strftime("%H:%M:%S"),
                                                     time.strftime("%d/%m/%y")))

        if not self.config.save_videos and os.path.isdir(AUDIO_CACHE_PATH):
            if self._delete_old_audiocache():
                print("Deleting old audio cache")
                await self.log(":mega: The audio cache was cleared")
            else:
                print("Could not delete old audio cache, moving on.")
                await self.log(":warning: Tried to clear audio cache, encountered a problem")

        if self.config.autojoin_channels:
            await self._autojoin_channels()

        elif self.config.auto_summon:
            print("Attempting to autosummon...", flush=True)

            # waitfor + get value
            owner_vc = await self._auto_summon()

            if owner_vc:
                print("Done!", flush=True)  # TODO: Change this to "Joined server/channel"
                if self.config.auto_playlist:
                    print("Starting auto-playlist")
                    await self.on_finished_playing(await self.get_player(owner_vc))
            else:
                print("Owner not found in a voice channel, could not autosummon.")
                if self.config.log_exceptions:
                    await self.log(":warning: Tried to autosummon, owner not found in a channel")

        print()
        print('---------------------------------------')
        # t-t-th-th-that's all folks!

    async def cmd_whitelist(self, message, option, username):
        """
        Usage:
            {command_prefix}whitelist [ + | - | add | remove ] @UserName

        Adds or removes the user to the whitelist.
        When the whitelist is enabled, whitelisted users are permitted to use bot commands.
        """

        user_id = extract_user_id(username)
        if not user_id:
            raise exceptions.CommandError('Invalid user specified')

        if option not in ['+', '-', 'add', 'remove']:
            raise exceptions.CommandError(
                'Invalid switch "%s" used, use +, -, add, or remove' % option, expire_in=20
            )

        if option in ['+', 'add']:
            self.whitelist.add(user_id)
            write_file(self.config.whitelist_file, self.whitelist)

            return Response('user has been added to the whitelist', reply=True, delete_after=10)

        else:
            if user_id not in self.whitelist:
                return Response('user is not in the whitelist', reply=True, delete_after=10)

            else:
                self.whitelist.remove(user_id)
                write_file(self.config.whitelist_file, self.whitelist)

                return Response('user has been removed from the whitelist', reply=True, delete_after=10)

    async def cmd_listchannels(self, server, author):
        """
        Usage: {command_prefix}listchannels

        List the channels on the server for setting up permissions
        """
        if not self._check_server_exist(server):
            return await self.send_message(author, 'You cannot use this bot in private messages.')

        lines = ['Channel list for %s' % server.name, '```', '```']
        for channel in server.channels:
            nextline = channel.id + ' ' + channel.name
            if len('\n'.join(lines)) + len(nextline) < DISCORD_MSG_CHAR_LIMIT:
                lines.insert(len(lines) - 1, nextline)
            else:
                await self.send_message(author, '\n'.join(lines))
                lines = ['```', '```']
        await self.send_message(author, '\n'.join(lines))
        return Response("Check your DMs")

    async def cmd_listroles(self, server, author):
        """
        Usage: {command_prefix}listroles
        Lists the roles on the server for setting up permissions
        """
        if not self._check_server_exist(server):
            return await self.send_message(author, 'You cannot use this bot in private messages.')

        lines = ['Role list for %s' % server.name, '```', '```']
        for role in server.roles:
            role.name = role.name.replace('@everyone', '@\u200Beveryone')  # ZWS for sneaky names
            nextline = role.id + " " + role.name

            if len('\n'.join(lines)) + len(nextline) < DISCORD_MSG_CHAR_LIMIT:
                lines.insert(len(lines) - 1, nextline)
            else:
                await self.send_message(author, '\n'.join(lines))
                lines = ['```', '```']

        await self.send_message(author, '\n'.join(lines))
        return Response("Check your DMs")

    def _check_server_exist(self, server):
        if server is not None:
            return True
        return False

    async def cmd_blacklist(self, message, option, username):
        """
        Usage:
            {command_prefix}blacklist [ + | - | add | remove ] @UserName

        Adds or removes the user to the blacklist.
        Blacklisted users are forbidden from using bot commands. Blacklisting a user also removes them from the whitelist.
        """

        user_id = extract_user_id(username)
        if not user_id:
            raise exceptions.CommandError('Invalid user specified', expire_in=30)

        if str(user_id) == self.config.owner_id:
            return Response("You can\'t blacklist the owner, you dingus", delete_after=10)

        if option not in ['+', '-', 'add', 'remove']:
            raise exceptions.CommandError(
                'Invalid switch "%s" used, use +, -, add, or remove' % option, expire_in=20
            )

        if option in ['+', 'add']:
            self.blacklist.add(user_id)
            write_file(self.config.blacklist_file, self.blacklist)

            if user_id in self.whitelist:
                self.whitelist.remove(user_id)
                write_file(self.config.whitelist_file, self.whitelist)
                return Response(
                    'user has been added to the blacklist and removed from the whitelist',
                    reply=True, delete_after=10
                )

            else:
                return Response('user has been added to the blacklist', reply=True, delete_after=10)

        else:
            if user_id not in self.blacklist:
                return Response('user is not in the blacklist', reply=True, delete_after=10)

            else:
                self.blacklist.remove(user_id)
                write_file(self.config.blacklist_file, self.blacklist)

                return Response('user has been removed from the blacklist', reply=True, delete_after=10)

    async def cmd_id(self, author, user_mentions):
        """
        Usage:
            {command_prefix}id [@user]

        Tells the user their id or the id of another user.
        """
        if not user_mentions:
            return Response('your Discord ID is: `%s`' % author.id, reply=True, delete_after=35)
        else:
            usr = user_mentions[0]
            return Response("%s's Discord ID is: `%s`" % (usr.name, usr.id), reply=True, delete_after=35)

    async def cmd_compspecs(self, message):
        """
        Usage: {command_prefix}compspecs
        Displays the computer specs currently running this bot
        """
        platform = 'Platform: ' + str(self.platform.getPlatform())
        platformVersion = 'Version: ' + str(self.platform.getVersion())
        platformMachine = 'Machine: ' + str(self.platform.getMachine())
        platformUName = 'Specs: ' + str(self.platform.getPlatUName())
        platformSys = 'Sys: ' + str(self.platform.getSys())
        platformProcessor = 'Processor: ' + str(self.platform.getProcessor())
        compSpecs = '**PC Specs**:'
        compSpecs += '\n\t' + platform
        compSpecs += '\n\t' + platformVersion
        compSpecs += '\n\t' + platformMachine
        compSpecs += '\n\t' + platformUName
        compSpecs += '\n\t' + platformSys
        compSpecs += '\n\t' + platformProcessor
        return Response(compSpecs, reply=True)

    async def cmd_joinserver(self, message):
        """
        Usage:
            {command_prefix}joinserver
        Tells you how to join a server.

        OAuth Link:  http://inv.rtb.dragonfire.me
        """
        return Response("http://inv.rtb.dragonfire.me - OAuth Link - If it doesn't work, report with .notifydev",
                        delete_after=0)

    async def cmd_play(self, player, channel, author, permissions, leftover_args, song_url):
        """
        Usage:
            {command_prefix}play song_link
            {command_prefix}play text to search for

        Adds the song to the playlist.  If a link is not provided, the first
        result from a youtube search is added to the queue.
        """

        song_url = song_url.strip('<>')

        if permissions.max_songs and player.playlist.count_for_user(author) >= permissions.max_songs:
            raise exceptions.PermissionsError(
                "You have reached your playlist item limit (%s)" % permissions.max_songs, expire_in=30
            )

        await self.send_typing(channel)

        if leftover_args:
            song_url = ' '.join([song_url, *leftover_args])

        try:
            info = await self.downloader.extract_info(player.playlist.loop, song_url, download=False, process=False)
        except Exception as e:
            raise exceptions.CommandError(e, expire_in=30)

        if not info:
            raise exceptions.CommandError("That video cannot be played.", expire_in=30)

        # abstract the search handling away from the user
        # our ytdl options allow us to use search strings as input urls
        if info.get('url', '').startswith('ytsearch'):
            # print("[Command:play] Searching for \"%s\"" % song_url)
            info = await self.downloader.extract_info(
                player.playlist.loop,
                song_url,
                download=False,
                process=True,  # ASYNC LAMBDAS WHEN
                on_error=lambda e: asyncio.ensure_future(
                    self.safe_send_message(channel, "```\n%s\n```" % e, expire_in=120), loop=self.loop),
                retry_on_error=True
            )

            if not info:
                raise exceptions.CommandError(
                    "Error extracting info from search string, youtubedl returned no data.  "
                    "You may need to restart the bot if this continues to happen.", expire_in=30
                )

            if not all(info.get('entries', [])):
                # empty list, no data
                return

            song_url = info['entries'][0]['webpage_url']
            info = await self.downloader.extract_info(player.playlist.loop, song_url, download=False, process=False)
            # Now I could just do: return await self.cmd_play(player, channel, author, song_url)
            # But this is probably fine

        # TODO: Possibly add another check here to see about things like the bandcamp issue
        # TODO: Where ytdl gets the generic extractor version with no processing, but finds two different urls

        if 'entries' in info:
            # I have to do exe extra checks anyways because you can request an arbitrary number of search results
            if not permissions.allow_playlists and ':search' in info['extractor'] and len(info['entries']) > 1:
                raise exceptions.PermissionsError("You are not allowed to request playlists", expire_in=30)

            # The only reason we would use this over `len(info['entries'])` is if we add `if _` to this one
            num_songs = sum(1 for _ in info['entries'])

            if permissions.max_playlist_length and num_songs > permissions.max_playlist_length:
                raise exceptions.PermissionsError(
                    "Playlist has too many songs. (%s > %s)" % (num_songs, permissions.max_playlist_length),
                    expire_in=30
                )

            # This is a little bit weird when it says (x + 0 > y), I might add the other check back in
            if permissions.max_songs and player.playlist.count_for_user(author) + num_songs > permissions.max_songs:
                raise exceptions.PermissionsError(
                    "Playlist entries + your already queued songs reached limit (%s + %s > %s)" % (
                        num_songs, player.playlist.count_for_user(author), permissions.max_songs),
                    expire_in=30
                )

            if info['extractor'].lower() in ['youtube:playlist', 'soundcloud:set', 'bandcamp:album']:
                try:
                    return await self._cmd_play_playlist_async(player, channel, author, permissions, song_url,
                                                               info['extractor'])
                except exceptions.CommandError:
                    raise
                except Exception as e:
                    traceback.print_exc()
                    raise exceptions.CommandError("Error queuing playlist:\n%s" % e, expire_in=30)

            t0 = time.time()

            # My test was 1.2 seconds per song, but we maybe should fudge it a bit, unless we can
            # monitor it and edit the message with the estimated time, but that's some ADVANCED SHIT
            # I don't think we can hook into it anyways, so this will have to do.
            # It would probably be a thread to check a few playlists and get the speed from that
            # Different playlists might download at different speeds though
            wait_per_song = 1.2

            procmesg = await self.safe_send_message(
                channel,
                'Gathering playlist information for {} songs{}'.format(
                    num_songs,
                    ', ETA: {} seconds'.format(self._fixg(
                        num_songs * wait_per_song)) if num_songs >= 10 else '.'))

            # We don't have a pretty way of doing this yet.  We need either a loop
            # that sends these every 10 seconds or a nice context manager.
            await self.send_typing(channel)

            # TODO: I can create an event emitter object instead, add event functions, and every play list might be asyncified
            #       Also have a "verify_entry" hook with the entry as an arg and returns the entry if its ok

            entry_list, position = await player.playlist.import_from(song_url, channel=channel, author=author)

            tnow = time.time()
            ttime = tnow - t0
            listlen = len(entry_list)
            drop_count = 0

            if permissions.max_song_length:
                for e in entry_list.copy():
                    if e.duration > permissions.max_song_length:
                        player.playlist.entries.remove(e)
                        entry_list.remove(e)
                        drop_count += 1
                        # Im pretty sure there's no situation where this would ever break
                        # Unless the first entry starts being played, which would make this a race condition
                if drop_count:
                    print("Dropped %s songs" % drop_count)

            print("Processed {} songs in {} seconds at {:.2f}s/song, {:+.2g}/song from expected ({}s)".format(
                listlen,
                self._fixg(ttime),
                ttime / listlen,
                ttime / listlen - wait_per_song,
                self._fixg(wait_per_song * num_songs))
            )

            await self.safe_delete_message(procmesg)

            if not listlen - drop_count:
                raise exceptions.CommandError(
                    "No songs were added, all songs were over max duration (%ss)" % permissions.max_song_length,
                    expire_in=30
                )

            reply_text = "Added **%s** songs to be played. Position in queue list: %s"
            btext = str(listlen - drop_count)

        else:
            if permissions.max_song_length and info.get('duration', 0) > permissions.max_song_length:
                raise exceptions.PermissionsError(
                    "Song duration exceeds limit (%s > %s)" % (info['duration'], permissions.max_song_length),
                    expire_in=30
                )

            try:
                entry, position = await player.playlist.add_entry(song_url, channel=channel, author=author)

            except exceptions.WrongEntryTypeError as e:
                if e.use_url == song_url:
                    print("[Warning] Determined incorrect entry type, but suggested url is the same.  Help.")

                if self.config.debug_mode:
                    print("[Info] Assumed url \"%s\" was a single entry, was actually a playlist" % song_url)
                    print("[Info] Using \"%s\" instead" % e.use_url)

                return await self.cmd_play(player, channel, author, permissions, leftover_args, e.use_url)

            reply_text = "Added **%s** to be played. Position in queue list: %s"
            btext = entry.title

        if position == 1 and player.is_stopped:
            position = 'Up next!'
            reply_text %= (btext, position)

        else:
            try:
                time_until = await player.playlist.estimate_time_until(position, player)
                reply_text += ' - estimated time until playing: %s'
            except:
                traceback.print_exc()
                time_until = ''

            reply_text %= (btext, position, time_until)

        return Response(reply_text, delete_after=30)

    async def _cmd_play_playlist_async(self, player, channel, author, permissions, playlist_url, extractor_type):
        """
        Secret handler to use the async wizardry to make playlist queuing non-"blocking"
        """

        await self.send_typing(channel)
        info = await self.downloader.extract_info(player.playlist.loop, playlist_url, download=False, process=False)

        if not info:
            raise exceptions.CommandError("That playlist cannot be played.")

        num_songs = sum(1 for _ in info['entries'])
        t0 = time.time()

        busymsg = await self.safe_send_message(
            channel, "Processing %s songs..." % num_songs)  # TODO: From playlist_title
        await self.send_typing(channel)

        if extractor_type == 'youtube:playlist':
            try:
                entries_added = await player.playlist.async_process_youtube_playlist(
                    playlist_url, channel=channel, author=author)
                # TODO: Add hook to be called after each song
                # TODO: Add permissions

            except Exception:
                traceback.print_exc()
                raise exceptions.CommandError('Error handling playlist %s queuing.' % playlist_url, expire_in=30)

        elif extractor_type.lower() in ['soundcloud:set', 'bandcamp:album']:
            try:
                entries_added = await player.playlist.async_process_sc_bc_playlist(
                    playlist_url, channel=channel, author=author)
                # TODO: Add hook to be called after each song
                # TODO: Add permissions

            except Exception:
                traceback.print_exc()
                raise exceptions.CommandError('Error handling playlist %s queuing.' % playlist_url, expire_in=30)

        songs_processed = len(entries_added)
        drop_count = 0
        skipped = False

        if permissions.max_song_length:
            for e in entries_added.copy():
                if e.duration > permissions.max_song_length:
                    try:
                        player.playlist.entries.remove(e)
                        entries_added.remove(e)
                        drop_count += 1
                    except:
                        pass

            if drop_count:
                print("Dropped %s songs" % drop_count)

            if player.current_entry and player.current_entry.duration > permissions.max_song_length:
                await self.safe_delete_message(self.server_specific_data[channel.server]['last_np_msg'])
                self.server_specific_data[channel.server]['last_np_msg'] = None
                skipped = True
                player.skip()
                entries_added.pop()

        await self.safe_delete_message(busymsg)

        songs_added = len(entries_added)
        tnow = time.time()
        ttime = tnow - t0
        wait_per_song = 1.2
        # TODO: actually calculate wait per song in the process function and return that too

        # This is technically inaccurate since bad songs are ignored but still take up time
        print("Processed {}/{} songs in {} seconds at {:.2f}s/song, {:+.2g}/song from expected ({}s)".format(
            songs_processed,
            num_songs,
            self._fixg(ttime),
            ttime / num_songs,
            ttime / num_songs - wait_per_song,
            self._fixg(wait_per_song * num_songs))
        )

        if not songs_added:
            basetext = "No songs were added, all songs were over max duration (%ss)" % permissions.max_song_length
            if skipped:
                basetext += "\nAdditionally, the current song was skipped for being too long."

            raise exceptions.CommandError(basetext, expire_in=30)

        return Response("Enqueued {} songs to be played in {} seconds".format(
            songs_added, self._fixg(ttime, 1)), delete_after=30)

    async def cmd_search(self, player, channel, author, permissions, leftover_args):
        """
        Usage:
            {command_prefix}search [service] [number] query

        Searches a service for a video and adds it to the queue.
        - service: any one of the following services:
            - youtube (yt) (default if unspecified)
            - soundcloud (sc)
            - yahoo (yh)
        - number: return a number of video results and waits for user to choose one
          - defaults to 1 if unspecified
          - note: If your search query starts with a number,
                  you must put your query in quotes
            - ex: {command_prefix}search 2 "I ran seagulls"
        """

        if permissions.max_songs and player.playlist.count_for_user(author) > permissions.max_songs:
            raise exceptions.PermissionsError(
                "You have reached your playlist item limit (%s)" % permissions.max_songs,
                expire_in=30
            )

        def argcheck():
            if not leftover_args:
                raise exceptions.CommandError(
                    "Please specify a search query.\n%s" % dedent(
                        self.cmd_search.__doc__.format(command_prefix=self.config.command_prefix)),
                    expire_in=60
                )

        argcheck()

        try:
            leftover_args = shlex.split(' '.join(leftover_args))
        except ValueError:
            raise exceptions.CommandError("Please quote your search query properly.", expire_in=30)

        service = 'youtube'
        items_requested = 3
        max_items = 10  # this can be whatever, but since ytdl uses about 1000, a small number might be better
        services = {
            'youtube': 'ytsearch',
            'soundcloud': 'scsearch',
            'yahoo': 'yvsearch',
            'yt': 'ytsearch',
            'sc': 'scsearch',
            'yh': 'yvsearch'
        }

        if leftover_args[0] in services:
            service = leftover_args.pop(0)
            argcheck()

        if leftover_args[0].isdigit():
            items_requested = int(leftover_args.pop(0))
            argcheck()

            if items_requested > max_items:
                raise exceptions.CommandError("You cannot search for more than %s videos" % max_items)

        # Look jake, if you see this and go "what the fuck are you doing"
        # and have a better idea on how to do this, i'd be delighted to know.
        # I don't want to just do ' '.join(leftover_args).strip("\"'")
        # Because that eats both quotes if they're there
        # where I only want to eat the outermost ones
        if leftover_args[0][0] in '\'"':
            lchar = leftover_args[0][0]
            leftover_args[0] = leftover_args[0].lstrip(lchar)
            leftover_args[-1] = leftover_args[-1].rstrip(lchar)

        search_query = '%s%s:%s' % (services[service], items_requested, ' '.join(leftover_args))

        search_msg = await self.send_message(channel, "Searching for videos...")
        await self.send_typing(channel)

        try:
            info = await self.downloader.extract_info(player.playlist.loop, search_query, download=False, process=True)

        except Exception as e:
            await self.safe_edit_message(search_msg, str(e), send_if_fail=True)
            return
        else:
            await self.safe_delete_message(search_msg)

        if not info:
            return Response("No videos found.", delete_after=30)

        def check(m):
            return (
                m.content.lower()[0] in 'yn' or
                # hardcoded function name weeee
                m.content.lower().startswith('{}{}'.format(self.config.command_prefix, 'search')) or
                m.content.lower().startswith('exit'))

        for e in info['entries']:
            result_message = await self.safe_send_message(channel, "Result %s/%s: %s" % (
                info['entries'].index(e) + 1, len(info['entries']), e['webpage_url']))

            confirm_message = await self.safe_send_message(channel, "Is this ok? Type `y`, `n` or `exit`")
            response_message = await self.wait_for_message(30, author=author, channel=channel, check=check)

            if not response_message:
                await self.safe_delete_message(result_message)
                await self.safe_delete_message(confirm_message)
                return Response("Ok nevermind.", delete_after=30)

            # They started a new search query so lets clean up and bugger off
            elif response_message.content.startswith(self.config.command_prefix) or \
                    response_message.content.lower().startswith('exit'):

                await self.safe_delete_message(result_message)
                await self.safe_delete_message(confirm_message)
                return

            if response_message.content.lower().startswith('y'):
                await self.safe_delete_message(result_message)
                await self.safe_delete_message(confirm_message)
                await self.safe_delete_message(response_message)

                await self.cmd_play(player, channel, author, permissions, [], e['webpage_url'])

                return Response("Alright, coming right up!", delete_after=30)
            else:
                await self.safe_delete_message(result_message)
                await self.safe_delete_message(confirm_message)
                await self.safe_delete_message(response_message)

        return Response("Oh well :frowning:", delete_after=30)

    async def cmd_np(self, player, channel, server, message):
        """
        Usage:
            {command_prefix}np

        Displays the current song in chat.
        """

        if player.current_entry:
            if self.server_specific_data[server]['last_np_msg']:
                await self.safe_delete_message(self.server_specific_data[server]['last_np_msg'])
                self.server_specific_data[server]['last_np_msg'] = None

            song_progress = str(timedelta(seconds=player.progress)).lstrip('0').lstrip(':')
            song_total = str(timedelta(seconds=player.current_entry.duration)).lstrip('0').lstrip(':')
            prog_str = '`[%s/%s]`' % (song_progress, song_total)

            if player.current_entry.meta.get('channel', False) and player.current_entry.meta.get('author', False):
                np_text = "Now Playing: **%s** added by **%s** %s\n" % (
                    player.current_entry.title, player.current_entry.meta['author'].name, prog_str)
            else:
                np_text = "Now Playing: **%s** %s\n" % (player.current_entry.title, prog_str)

            self.server_specific_data[server]['last_np_msg'] = await self.safe_send_message(channel, np_text)
            await self._manual_delete_check(message)
        else:
            return Response(
                'There are no songs queued! Queue something with {}play.'.format(self.config.command_prefix),
                delete_after=30
            )

    async def cmd_summon(self, message, channel, author, voice_channel):
        """
        Usage:
            {command_prefix}summon

        Call the bot to the summoner's voice channel.
        """

        if not author.voice_channel:
            raise exceptions.CommandError(
                "Get your lazy good for nothing ass in a voice channel before giving me demands bitch. (AUTHOR_NOT_IN_CHANNEL)")

        voice_client = self.the_voice_clients.get(channel.server.id, None)
        if voice_client and voice_client.channel.server == author.voice_channel.server:
            await self.safe_send_message(message.channel, "Joined ***" + message.author.voice_channel.name + "***.")
            await self.move_voice_client(author.voice_channel)
            return

        # move to _verify_vc_perms?
        chperms = author.voice_channel.permissions_for(author.voice_channel.server.me)

        if not chperms.connect:
            self.safe_print("Cannot join channel \"%s\", no permission." % author.voice_channel.name)
            return Response(
                "```Cannot join channel \"%s\", no permission.```" % author.voice_channel.name,
                delete_after=25
            )

        elif not chperms.speak:
            self.safe_print("Will not join channel \"%s\", no permission to speak." % author.voice_channel.name)
            return Response(
                "```Will not join channel \"%s\", no permission to speak.```" % author.voice_channel.name,
                delete_after=25
            )

        player = await self.get_player(author.voice_channel, create=True)

        if player.is_stopped:
            player.play()

        if self.config.auto_playlist:
            await self.on_finished_playing(player)

    async def cmd_pause(self, message, player):
        """
        Usage:
            {command_prefix}pause

        Pauses playback of the current song.
        """

        if player.is_playing:
            await self.safe_send_message(message.channel, "Song paused.")
            player.pause()

        else:
            raise exceptions.CommandError("I'm not playing anything.", expire_in=30)

    async def cmd_resume(self, message, player):
        """
        Usage:
            {command_prefix}resume

        Resumes playback of a paused song.
        """

        if player.is_paused:
            await self.safe_send_message(message.channel, "Song resumed.")
            player.resume()

        else:
            raise exceptions.CommandError("I'm not playing anything, nor its not paused.", expire_in=30)

    async def cmd_shuffle(self, channel, player):
        """
        Usage:
            {command_prefix}shuffle

        Shuffles the playlist.
        """

        player.playlist.shuffle()

        cards = [':spades:', ':clubs:', ':hearts:', ':diamonds:']
        hand = await self.send_message(channel, ' '.join(cards))
        await asyncio.sleep(0.6)

        for x in range(4):
            shuffle(cards)
            await self.safe_edit_message(hand, ' '.join(cards))
            await asyncio.sleep(0.6)

        await self.safe_delete_message(hand, quiet=True)
        return Response(":ok_hand: shuffled af", delete_after=15)

    async def cmd_clear(self, player, author):
        """
        Usage:
            {command_prefix}clear

        Clears the playlist.
        """

        player.playlist.clear()
        return Response(
            'Cleared the playlist.... I bet there\'s some stupid songs in there that killed it. Oh well, what happen must happen.',
            delete_after=20)

    async def cmd_skip(self, player, channel, author, message, permissions, voice_channel):
        """
        Usage:
            {command_prefix}skip

        Skips the current song when enough votes are cast, or by the bot owner.
        """

        if player.is_stopped:
            raise exceptions.CommandError("Can't skip....? I'm not playing anything!", expire_in=20)

        if not player.current_entry:
            if player.playlist.peek():
                if player.playlist.peek()._is_downloading:
                    print(player.playlist.peek()._waiting_futures[0].__dict__)
                    return Response("The next song (%s) is downloading, please wait." % player.playlist.peek())

                elif player.playlist.peek().is_downloaded:
                    print("The next song will be played shortly.  Please wait.")
                else:
                    print("Something odd is happening.  "
                          "You might want to restart the bot if it doesn't start working.")
            else:
                print("Something strange is happening.  "
                      "You might want to restart the bot if it doesn't start working.")

        if author.id == self.config.owner_id or permissions.instaskip:
            player.skip()  # check autopause stuff here
            await self._manual_delete_check(message)
            return

        # TODO: ignore person if they're deaf or take them out of the list or something?
        # Currently is recounted if they vote, deafen, then vote

        num_voice = sum(1 for m in voice_channel.voice_members if not (
            m.deaf or m.self_deaf or m.id in [self.config.owner_id, self.user.id]))

        num_skips = player.skip_state.add_skipper(author.id, message)

        skips_remaining = min(self.config.skips_required,
                              sane_round_int(num_voice * self.config.skip_ratio_required)) - num_skips

        if skips_remaining <= 0:
            player.skip()  # check autopause stuff here
            return Response(
                'your skip for **{}** was acknowledged.'
                '\nThe vote to skip has been passed.{}'.format(
                    player.current_entry.title,
                    ' Next song coming up!' if player.playlist.peek() else ''
                ),
                reply=True,
                delete_after=20
            )

        else:
            # TODO: When a song gets skipped, delete the old x needed to skip messages
            return Response(
                'your skip for **{}** was acknowledged.'
                '\n**{}** more {} required to vote to skip this song.'.format(
                    player.current_entry.title,
                    skips_remaining,
                    'person is' if skips_remaining == 1 else 'people are'
                ),
                reply=True,
                delete_after=20
            )

    async def cmd_volume(self, message, player, new_volume=None):
        """
        Usage:
            {command_prefix}volume (+/-)[volume]

        Sets the playback volume. Accepted values are from 1 to 200.
        Putting + or - before the volume will make the volume change relative to the current volume.
        Volume past 100% is now accepted, but only use it if you want earbusting earrape.
        """

        if not new_volume:
            return Response('Current volume: `%s%%`' % int(player.volume * 200), reply=True, delete_after=20)

        relative = False
        if new_volume[0] in '+-':
            relative = True

        try:
            new_volume = int(new_volume)

        except ValueError:
            raise exceptions.CommandError(
                '{} <-- Really? I know you can do better. It\'s obviously some shameful decimal number, or it\'s not a fucking number. Think harder next time.'.format(
                    new_volume), expire_in=20)

        if relative:
            vol_change = new_volume
            new_volume += (player.volume * 200)

        old_volume = int(player.volume * 200)

        if 0 < new_volume <= 200:
            player.volume = new_volume / 200.0

            return Response('updated volume from %d to %d' % (old_volume, new_volume), reply=True, delete_after=20)

        else:
            if relative:
                raise exceptions.CommandError(
                    'Unreasonable volume change provided: {}{:+} -> {}%.  Provide a change between {} and {:+}.'.format(
                        old_volume, vol_change, old_volume + vol_change, 1 - old_volume, 200 - old_volume),
                    expire_in=20)
            else:
                raise exceptions.CommandError(
                    'Unreasonable volume provided: {}%. Choose a number that\'s 1-200.'.format(new_volume),
                    expire_in=20)

    async def cmd_queue(self, channel, player):
        """
        Usage:
            {command_prefix}queue

        Prints the current song queue.
        """

        lines = []
        unlisted = 0
        andmoretext = '* ... and %s more*' % ('x' * len(player.playlist.entries))

        if player.current_entry:
            song_progress = str(timedelta(seconds=player.progress)).lstrip('0').lstrip(':')
            song_total = str(timedelta(seconds=player.current_entry.duration)).lstrip('0').lstrip(':')
            prog_str = '`[%s/%s]`' % (song_progress, song_total)

            if player.current_entry.meta.get('channel', False) and player.current_entry.meta.get('author', False):
                lines.append("Now Playing: **%s** added by **%s** %s\n" % (
                    player.current_entry.title, player.current_entry.meta['author'].name, prog_str))
            else:
                lines.append("Now Playing: **%s** %s\n" % (player.current_entry.title, prog_str))

        for i, item in enumerate(player.playlist, 1):
            if item.meta.get('channel', False) and item.meta.get('author', False):
                nextline = '`{}.` **{}** added by **{}**'.format(i, item.title, item.meta['author'].name).strip()
            else:
                nextline = '`{}.` **{}**'.format(i, item.title).strip()

            currentlinesum = sum(len(x) + 1 for x in lines)  # +1 is for newline char

            if currentlinesum + len(nextline) + len(andmoretext) > DISCORD_MSG_CHAR_LIMIT:
                if currentlinesum + len(andmoretext):
                    unlisted += 1
                    continue

            lines.append(nextline)

        if unlisted:
            lines.append('\n*... and %s more*' % unlisted)

        if not lines:
            lines.append(
                'No songs, queue something with {}play.'.format(self.config.command_prefix))

        message = '\n'.join(lines)
        return Response(message, delete_after=30)

    async def cmd_clean(self, message, channel, author, search_range=50):
        """
        Usage:
            {command_prefix}clean [range]

        Removes up to [range] messages the bot has posted in chat. Default: 50, Max: 1000
        """

        try:
            float(search_range)  # lazy check
            search_range = min(int(search_range), 1000)
        except:
            return Response("enter. a number. ***A NUMBER.*** like `100`. pls.", reply=True, delete_after=8)

        await self.safe_delete_message(message, quiet=True)

        def is_possible_command_invoke(entry):
            valid_call = any(
                entry.content.startswith(prefix) for prefix in [self.config.command_prefix])  # can be expanded
            return valid_call and not entry.content[1:2].isspace()

        msgs = 0
        delete_invokes = True
        delete_all = channel.permissions_for(author).manage_messages or self.config.owner_id == author.id

        async for entry in self.logs_from(channel, search_range, before=message):
            if entry == self.server_specific_data[channel.server]['last_np_msg']:
                continue

            if entry.author == self.user:
                await self.safe_delete_message(entry)
                msgs += 1

            if is_possible_command_invoke(entry) and delete_invokes:
                if delete_all or entry.author == author:
                    try:
                        await self.delete_message(entry)
                        await asyncio.sleep(.35)
                        msgs += 1
                    except discord.Forbidden:
                        delete_invokes = False
                    except discord.HTTPException:
                        return Response("Being rate limited, yeah.", delete_after=0)
        if self.config.log_interaction:
            await self.log(
                ':bomb: Purged `{}` message{} in #`{}`'.format(len(deleted), 's' * bool(deleted), channel.name),
                channel)
        return Response('Cleaned up {} message{}.'.format(msgs, '' if msgs == 1 else 's'), delete_after=15)

    async def cmd_pldump(self, channel, song_url):
        """
        Usage:
            {command_prefix}pldump url

        Dumps the individual urls of a playlist
        """

        try:
            info = await self.downloader.extract_info(self.loop, song_url.strip('<>'), download=False, process=False)
        except Exception as e:
            raise exceptions.CommandError("Could not extract info from input url\n%s\n" % e, expire_in=25)

        if not info:
            raise exceptions.CommandError("Could not extract info from input url, no data.", expire_in=25)

        if not info.get('entries', None):
            # TODO: Retarded playlist checking
            # set(url, webpageurl).difference(set(url))

            if info.get('url', None) != info.get('webpage_url', info.get('url', None)):
                raise exceptions.CommandError("This does not seem to be a playlist.", expire_in=25)
            else:
                return await self.cmd_pldump(channel, info.get(''))

        linegens = defaultdict(lambda: None, **{
            "youtube": lambda d: 'https://www.youtube.com/watch?v=%s' % d['id'],
            "soundcloud": lambda d: d['url'],
            "bandcamp": lambda d: d['url']
        })

        exfunc = linegens[info['extractor'].split(':')[0]]

        if not exfunc:
            raise exceptions.CommandError("Could not extract info from input url, unsupported playlist type.",
                                          expire_in=25)

        with BytesIO() as fcontent:
            for item in info['entries']:
                fcontent.write(exfunc(item).encode('utf8') + b'\n')

            fcontent.seek(0)
            await self.send_file(channel, fcontent, filename='playlist.txt',
                                 content="Here's the url dump for <%s>" % song_url)

        return Response(":mailbox_with_mail:", delete_after=20)

    async def cmd_listids(self, server, author, leftover_args, cat='all'):
        """
        Usage:
            {command_prefix}listids [categories]

        Lists the ids for various things.  Categories are:
           all, users, roles, channels
        """

        cats = ['channels', 'roles', 'users']

        if cat not in cats and cat != 'all':
            return Response(
                "Valid categories: " + ' '.join(['`%s`' % c for c in cats]),
                reply=True,
                delete_after=25
            )

        if cat == 'all':
            requested_cats = cats
        else:
            requested_cats = [cat] + [c.strip(',') for c in leftover_args]

        data = ['Your ID: %s' % author.id]

        for cur_cat in requested_cats:
            rawudata = None

            if cur_cat == 'users':
                data.append("\nUser IDs:")
                rawudata = ['%s #%s: %s' % (m.name, m.discriminator, m.id) for m in server.members]

            elif cur_cat == 'roles':
                data.append("\nRole IDs:")
                rawudata = ['%s: %s' % (r.name, r.id) for r in server.roles]

            elif cur_cat == 'channels':
                data.append("\nText Channel IDs:")
                tchans = [c for c in server.channels if c.type == discord.ChannelType.text]
                rawudata = ['%s: %s' % (c.name, c.id) for c in tchans]

                rawudata.append("\nVoice Channel IDs:")
                vchans = [c for c in server.channels if c.type == discord.ChannelType.voice]
                rawudata.extend('%s: %s' % (c.name, c.id) for c in vchans)

            if rawudata:
                data.extend(rawudata)

        with BytesIO() as sdata:
            sdata.writelines(d.encode('utf8') + b'\n' for d in data)
            sdata.seek(0)

            # TODO: Fix naming (Discord20API-ids.txt)
            await self.send_file(author, sdata, filename='%s-ids-%s.txt' % (server.name.replace(' ', '_'), cat))

        return Response("Check your PMs." + author, delete_after=20)

    async def cmd_perms(self, author, channel, server, permissions):
        """
        Usage:
            {command_prefix}perms

        Sends the user a list of their permissions.
        """

        lines = ['Command permissions in %s\n' % server.name, '```', '```']

        for perm in permissions.__dict__:
            if perm in ['user_list'] or permissions.__dict__[perm] == set():
                continue

            lines.insert(len(lines) - 1, "%s: %s" % (perm, permissions.__dict__[perm]))

        await self.send_message(author, '\n'.join(lines))
        return Response("Check them PMs fam", delete_after=20)

    async def cmd_kys(self, message):
        # return Response("kill yourself and never _EVER_ come back to me again, you stupid peasant. how dare you ask me to die. like fucking hell, why not do it yourself to satisfy yourself?", delete_after=0)
        return Response(
            "Seriously? You're such a fucking faggot. Kill yourself, unironically, hell, I'd kill you myself you fucking little shit, stupid fucking shitrag.",
            delete_after=0)
        # return Response("kill yourself and don't come back again to ask me to kill myself, stupid peasant.", delete_after=0)

    async def cmd_dab(self, message):
        return Response("​http://i.giphy.com/lae7QSMFxEkkE.gif", delete_after=0)

    @owner_only
    async def cmd_spamthefuckoutofeveryone(self, message):
        return Response(
            "( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°)( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°)",
            delete_after=0)

    async def cmd_memeg(author, self, message):
        """
        Attempt on trying to create a meme command, .memeg (template/line1/line2)
        List: http://memegen.link/templates/
        """
        genmeme = message.content[len(".memeg "):].strip()
        if message.content[len(".memeg"):].strip() != 0:
            return Response("http://memegen.link/" + re.sub(r"\s+", '-', genmeme) + ".jpg", delete_after=0)
        else:
            return Response("You didn't enter a message. Templates: http://memegen.link/templates/", delete_after=0)

    async def cmd_help2(self):
        """
        Usage:
            {command_prefix}help

        Prints a help message"""

        helpmsg = "**Commands**\n```"
        commands = []

        # TODO: Get this to format nicely
        for att in dir(self):
            if att.startswith('cmd_') and att != 'cmd_help':
                command_name = att.replace('cmd_', '').lower()
                commands.append("{}{}".format(self.config.command_prefix, command_name))

        helpmsg += ", ".join(commands)
        helpmsg += "```"
        helpmsg += "https://dragonfire.me/robtheboat/info.html"

        return Response(helpmsg, reply=True, delete_after=60)

    async def cmd_perf(self):
        rt = random.choice(tweetsthatareokhand)
        return Response(rt, delete_after=0)

    async def cmd_ver(self):
        return Response("`Ver. " + VER + " " + BUILD + "`", delete_after=0)

    # always remember to update this everytime you do an edit
    async def cmd_changes(self):
        return Response("What's new in " + VER + ": `changed .f to .pressf`", delete_after=0)

    async def cmd_setnick(self, server, channel, leftover_args, nick):
        """
        Usage:
            {command_prefix}setnick nick
        Changes the bot's nickname.
        """

        if not channel.permissions_for(server.me).change_nicknames:
            raise exceptions.CommandError("Unable to change nickname: no permission.")

        nick = ' '.join([nick, *leftover_args])

        try:
            await self.change_nickname(server.me, nick)
            await self.log(":warning: Bot name changed to `" + nick + "`" + " in %s" % server.name)
        except Exception as e:
            raise exceptions.CommandError(e, expire_in=20)

        return Response("Changed my nick to: `" + nick + "`", delete_after=20)

    @owner_only
    async def cmd_setavatar(self, message, url=None):
        """
        Usage:
            {command_prefix}setavatar [url]
        Changes the bot's avatar.
        Attaching a file and leaving the url parameter blank also works.
        """

        if message.attachments:
            thing = message.attachments[0]['url']
        else:
            thing = url.strip('<>')

        try:
            with aiohttp.Timeout(10):
                async with self.aiosession.get(thing) as res:
                    await self.edit_profile(avatar=await res.read())
        except Exception as e:
            raise exceptions.CommandError("Unable to change avatar: %s" % e, expire_in=20)

        return Response("Ooh, I look better in this picture, don't I?", delete_after=20)

    async def cmd_purge(self, message, author, server, channel, mentions, count=None, reason=None):
        """
        Usage: {command_prefix}purge <# of msgs to remove> @mention "<reason>"
        @mention is optional, same as for the reason.
        """
        if count and not reason and count.startswith('\"'):
            reason = count
            count = None
        await self.log(message, author, server, reason)
        if not mentions and not count:
            raise CommandError('Usage: {}purge <# of msgs to remove> @mention "<reason>'
                               'Removes all messages if a user isnt specified\n'
                               'If so, it removes the messages from the user.'.format(self.config.command_prefix))
        elif not mentions:
            try:
                count = int(count)
            except ValueError:
                raise CommandError('Invalid message count found : {}'.format(count))
            async for msg in self.logs_from(channel, count):
                await self.delete_message(msg)
        elif not count:
            if not mentions:
                raise CommandError('Invalid user specified')
            async for msg in self.logs_from(channel):
                if msg.author in mentions:
                    await self.delete_message(msg)
        elif count and mentions:
            try:
                count = int(count)
            except ValueError:
                raise CommandError('Invalid message count found : {}'.format(count))
            msg_count = 0
            async for msg in self.logs_from(channel):
                await self.log(
                    ':bomb: Purged `{}` message{} in #`{}`'.format(len(deleted), 's' * bool(deleted), channel.name),
                    channel)
                if msg.author in mentions and msg_count < count:
                    await self.delete_message(msg)
                    msg_count += 1

    async def cmd_ban(self, message, *members: discord.User):
        for user in members:
            try:
                await self.ban(discord.User, delete_message_days=7)
                await self.send_message(message.channel, user.name + " was rekterino from the server.")
            except discord.HTTPException:
                await self.send_message(message.channel,
                                        "Ban failed. Maybe you were trying to ban yourself or someone higher on the role chart?")

    @owner_only
    async def cmd_rtb(self, message, client):
        """
        RTB System.
        Only Wyndrik#0052 is allowed, or the Bot Owner if this isn't the main bot, RobTheBoat#9091
        """
        if message.content[len(".rtb "):].strip() == "servers":
            return Response("``` \n" + self.servers + "\n ```", delete_after=0)
        elif message.content[len(".rtb "):].strip() == "betamode":
            discord.Game(name='in Beta Mode')
            await self.change_status(discord.Game(name='in Beta Mode'))
            return Response("(!) Now in Beta mode.", delete_after=0)
        elif message.content[len(".rtb "):].strip() == "bye":
            await self.send_message(message.channel, "bye")
            await self.leave_server(message.channel)
        elif message.content[len(".rtb "):].strip() == "massren":
            return Response("NTS: Finish it.", delete_after=0)
        elif message.content[len(".rtb "):].strip() == "setgame":
            return Response("Use .setgame you idiotic nerd", delete_after=15)
        elif message.content[len(".rtb "):].strip() == "cleargame":
            await self.change_status(game=None)
            return Response("done", delete_after=15)
        elif message.content[len(".rtb "):].strip() == "listrtb":
            return Response(
                "Current switches: listrtb, setav, cleargame, cb selfspam, setgame, bye, betamode, servers, rename, dat boi, sysinfo",
                delete_after=15)
        elif message.content[len(".rtb "):].strip() == "dat boi":
            return Response("Ayy, it's dat boi!", delete_after=0)
        elif message.content[len(".rtb "):].strip() == "sysinfo":
            await self.safe_send_message(message.channel, platform.uname())
        elif message.content[len(".rtb "):].strip() == "cb selfspam":  # thanks lukkan99 fam
            cb = cleverbot.Cleverbot()
            iask = (cb.ask("*blushes.*"))
            while 1 == 1:
                await self.send_message(message.channel, iask)
                iask = (cb.ask(iask))
                asyncio.sleep(5)  # I need some kind of slowdown.
        elif message.content[len(".rtb "):].strip() == "gsh":
            discord.Game(name='.help for help!')

            await self.change_status(discord.Game(name='.help for help!'))

    async def cmd_e621(self, message):
        await self.send_message(message.channel,
                                "Look, I know you might be horny, but... Though I'm like some furry dragon and the developer is a furry, I'm not going to let you do this, literally, get your shit from the actual website, and get your lazy ass of Discord, and search.")
        asyncio.sleep(2)
        await self.send_message(message.channel,
                                "yeah, just uh... do that... and if you aren't horny... then, STOP TRYING.")
        await self.log(
            ":warning: lol attempted furry porn detected. Username: `{}` Server: `{}`".format(message.author.name,
                                                                                              message.server.name))
        # Drew's a furry, watch him be the first one to try this command.

    async def cmd_rule34(self, message):
        await self.send_message(message.channel,
                                "If you really want porn, there's the fucking internet. Like, there's Google Chrome and Mozilla Firefox. You can fap on those browsers. Even on mobile. Get your porn from somewhere else, pls.")
        await self.log(
            ":warning: lol attempted rule34 porn detected. Username: `{}` Server: `{}`".format(message.author.name,
                                                                                               message.server.name))
        # Watch Fardin be in this one first.

    async def cmd_yourinfo(self, message):
        try:
            if not message.content == message.content[len(".yourinfo "):].strip():
                target = message.author
                server = message.server
                inserver = str(
                    len(set([member.server.name for member in self.get_all_members() if member.name == target.name])))
                x = '```xl\n Your Player Data:\n Username: {0.name}\n ID: {0.id}\n Discriminator: {0.discriminator}\n Avatar URL: {0.avatar_url}\n Current Status: {2}\n Current Game: {3}\n Current VC: {4}\n Mutual servers: {1} \n They joined on: {5}\n Roles: {6}\n```'.format(
                    target, inserver, str(target.status), str(target.game), str(target.voice_channel),
                    str(target.joined_at), ', '.join(map(str, target.roles)).replace("@", "@\u200b"))
                await self.send_message(message.channel, x)
            elif message.content >= message.content[len(".yourinfo "):].strip():
                for user in discord.User:
                    server = message.server
                    inserver = str(
                        len(set([member.server.name for member in self.get_all_members() if member.name == user.name])))
                    x = '```xl\n Player Data:\n Username: {}\n ID: {}\n Discriminator: {}\n Avatar URL: {}\n Current Status: {}\n Current Game: {}\n Current VC: {}\n Mutual Servers: {}\n They joined on: {}\n Roles: {}\n```'.format(
                        user.name, user.id, user.discriminator, user.avatar_url, str(user.status), str(user.game),
                        str(user.voice_channel), inserver, str(user.joined_at),
                        ', '.join(map(str, user.roles)).replace("@", "@\u200b"))
                    await self.send_message(message.channel, x)
        except Exception as e:
            self.safe_send_message(message.channel, wrap.format(type(e).__name__ + ': ' + str(e)))

    async def cmd_serverdata(self, message):
        server = message.server
        if len(server.icon_url) < 1:
            url = "No icon set."
        else:
            url = server.icon_url
        await self.send_message(message.channel,
                                "```xl\n Server Data:\n Name: {0.name}\n ID: {0.id}\n Owner: {0.owner}\n Region: {0.region}\n Default Channel: {0.default_channel}\n Channels: {1}\n Members: {2}\n Roles: {3}\n Icon: {4}\n```".format(
                                    server, len(server.channels), len(server.members),
                                    ', '.join(map(str, server.roles)).replace("@", "@\u200b"), url))

    @owner_only
    async def cmd_renamebot(self, message):
        """
        Renames the bot.
            Part from the RTB System.
        """
        botrenamed = message.content[len(".renamebot "):].strip()
        await self.edit_profile(username=message.content[len(".renamebot "):].strip())
        return Response("Bot name changed to `" + botrenamed + "`", delete_after=5)
        if discord.errors.ClientException:
            return Response("Either you aren't a bot account, or you didn't put a name in. Either one.", delete_after=0)

    async def cmd_wiki(self, query: str, channel, message):
        """
        Wikipedia.
        Search the infinite pages!
        {}wikipedia (page)
        """
        cont2 = message.content[len(".wiki "):].strip()
        cont = re.sub(r"\s+", '_', query)
        q = wikipedia.page(cont)
        await self.send_typing(channel)
        await self.send_message(message.channel, "{}:\n```\n{}\n```\nFor more information, visit <{}>".format(q.title,
                                                                                                              wikipedia.summary(
                                                                                                                  query,
                                                                                                                  sentences=5),
                                                                                                              q.url))
        await self.safe_send_message(message.channel, cont)
        if wikipedia.exceptions.PageError == True:
            await self.safe_send_message(message.channel, "Error 404. Try another.")
        elif wikipedia.exceptions.DisambiguationError == True:
            await self.safe_send_message(message.channel, "Too many alike searches, please narrow it down more...")

    async def cmd_pressf(self, message):
        if message.content.startswith("f"):
            if message.server.id != "110373943822540800":
                await self.safe_send_message(message.channel, message.author.name + " has paid their respects.")
                await self.safe_send_message(message.channel, "Respects paid: " + str(random.randint(0, 1000)))
                await self.safe_send_message(message.channel, ":eggplant: :eggplant: :eggplant:")
        else:
            await self.safe_send_message(message.channel, message.author.name + " has paid their respects.")
            await self.safe_send_message(message.channel, "Respects paid: " + str(random.randint(0, 1000)))
            await self.safe_send_message(message.channel, ":eggplant: :eggplant: :eggplant:")

    @owner_only
    async def cmd_terminal(self, message):
        msg = check_output(message.content[len(".terminal "):].strip())
        await self.send_message(message.channel, xl.format(msg))

    @owner_only
    async def cmd_spam(self, message, times: int, lol):
        kek = copy.copy(lol)
        for i in range(times):
            await self.send_message(message.channel, kek)

    async def cmd_st(self, message):
        msg = check_output(["speedtest-cli", "--simple"]).decode()
        # --share
        await self.send_message(message.channel, xl.format(
            msg.replace("serverip", "Server IP").replace("\n", "\n").replace("\"", "").replace("b'", "").replace("'",
                                                                                                                 "")))

    async def cmd_ipping(self, message, ip: str):
        thing = check_output(["ping", "-c", "4", "{0}".format(ip)]).decode()
        await self.send_message(message.channel, xl.format(thing))

    async def cmd_rate(self, message):
        """
        Rate you or your idiot friends! They might not be idiots but still. It's with love <3
        {}rate (player/@mention/name/whatever)
        """
        drewisafurry = random.choice(ratelevel)  # I can't say how MUCH of a furry Drew is. Or known as Printendo
        if message.content[len(".rate "):].strip() == "<@163698730866966528>":
            await self.safe_send_message(message.channel,
                                         "I give myself a ***-1/10***, just because.")  # But guess what, Emil's a fucking furry IN DENIAL, so that's even worse. Don't worry, at least Drew's sane.
        elif message.content[len(".rate "):].strip() != "<@163698730866966528>":
            await self.safe_send_message(message.channel,
                                         "I give `" + message.content[len(".rate "):].strip().replace("@everyone",
                                                                                                      ">insert attempt to tag everyone here").replace(
                                             "@here",
                                             ">attempt to tag online users here") + "` a ***" + drewisafurry + "/10***")

    async def cmd_asshole(self, message):
        await self.send_file(message.channel, "imgs/asshole.jpg")

    async def cmd_lameme(self, message):
        await self.send_message(message.channel, "la meme xD xD xD")
        asyncio.sleep(5)
        await self.send_file(message.channel, "imgs/lameme.jpg")

    async def cmd_honk(self):
        return Response(random.choice(honkhonkfgt), delete_after=0)

    async def cmd_force(self):
        return Response("*forces*", delete_after=0)

    async def cmd_deny(self):
        return Response("fuckin denied amirite", delete_after=0)

    async def cmd_allow(self):
        return Response("bitch please allow what", delete_after=0)

    async def cmd_deformed(self, message):
        await self.send_file(message.channel, "imgs/deFORMED.PNG")
        await self.send_message(message.channel, "FUCKING DEFORMED.PNG")

    async def cmd_throw(self, message):
        if message.content[len(".throw "):].strip() == message.author.mention:
            return Response("throws " + random.choice(throwaf) + " towards you", delete_after=0)
        elif message.content == ".throw":
            return Response("throws " + random.choice(throwaf) + " towards you", delete_after=0)
        elif message.content[len(".throw "):].strip() == "<@!163698730866966528>":
            return Response("you are throwin ***NOTHIN*** to me, ok? ok.", delete_after=15)
        elif message.content[len(".throw "):].strip() != message.author.mention:
            return Response("throws " + random.choice(throwaf) + " to " + message.content[len(".throw "):].strip(),
                            delete_after=0)

    async def cmd_setgame(self, message):
        trashcan = name = message.content[len("setgame "):].strip()
        await self.send_typing(message.channel)
        discord.Game(name=message.content[len(".setgame "):].strip())
        await self.change_status(discord.Game(name=message.content[len("setgame "):].strip()))
        return Response("Successful, set as `" + trashcan + "`", delete_after=0)

    async def cmd_ping(self, message):
        pingtime = time.time()
        pingms = await self.send_message(message.channel, "pinging server...")
        ping = time.time() - pingtime
        await self.edit_message(pingms, "It took %.01f secs" % (ping) + " to ping.")
        # await self.edit_message(pingms, "hi. ` %ms`" % (ping[:-5]))

    @owner_only
    async def cmd_tdaily(self, message):
        await self.safe_send_message(message.channel, "t!daily <@117678528220233731>")

    @owner_only
    async def cmd_spamandkys(self, message):
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        await self.safe_send_message(message.channel, "Kys fag")
        if discord.HTTPException:
            await self.safe_send_message(message.channel,
                                         "I guess your spic fag self can't die. Fucking hell, I'm probably being rate limited, or something worse.")

    async def cmd_notifydev(self, message):
        if message.content > 10:
            await self.send_typing(message.channel)
            await self.send_message(message.channel, "Alerted.")
            await self.send_message(discord.User(id='117678528220233731'),
                                    "New message from `" + message.author.name + "` Discrim: `" + message.author.discriminator + "` ID: `" + message.author.id + "` Server Name: `" + message.author.server.name + "` Message: `" + message.content[
                                                                                                                                                                                                                                    len(
                                                                                                                                                                                                                                        ".notifydev "):].strip() + "`")
            await self.log(":information_source: Message sent to Wyndrik via the notifydev command: `" + message.content[len(".notifydev "):].strip() + "`")
        else:
            await self.send_message(message.channel, "You'd need to put a message in this....")

    async def cmd_ban(self, message, username):
        """
        Usage: {command_prefix}ban @Username
        Bans the user, and deletes 7 days of messages from the user prior to using the command.
        """
        user_id = extract_user_id(username)
        member = discord.utils.find(lambda mem: mem.id == str(user_id), message.channel.server.members)
        try:
            await self.ban(member, delete_message_days=7)
        except discord.Forbidden:
            return Response("You do not have the proper permissions to ban.", reply=True)
        except discord.HTTPException:
            return Response("Banning failed due to HTTPException error.", reply=True)

    async def cmd_unban(self, message, username):
        """
        Usage: {command_prefix}unban @Username
        Command to unban the user for 7 days if the bot has permissions to authorize
        """
        user_id = extract_user_id(username)
        member = discord.utils.find(lambda mem: mem.id == str(user_id), message.channel.server.members)
        try:
            await self.unban(member, delete_message_days=7)
        except discord.Forbidden:
            return Response("You do not have the proper permissions to unban.", reply=True)
        except discord.HTTPException:
                return Response("Unbanning failed due to HTTPException error.", reply=True)

    async def cmd_kick(self, message, username):
        """
        Usage: {command_prefix}kick @Username
        Command to kick the person from the server if the bot has permissions to authorize that kick
        """
        user_id = extract_user_id(username)
        member = discord.utils.find(lambda mem: mem.id == str(user_id), message.channel.server.members)
        try:
           await self.kick(member)
        except discord.Forbidden:
            return Response("You do not have the proper permissions to kick.", reply=True)
        except discord.HTTPException:
            return Response("Kicking failed due to HTTPException error.", reply=True)

    async def cmd_fursecute(self, message, mentions, fursona):
        """
        Fursecution! Command totally not stolen from some Minecraft server.
        .fursecute @mention "furry species"
        """
        fursona = message.content[len(".fursecute " + mentions):].strip()
        await self.send_typing(message.channel)
        asyncio.sleep(15)
        await self.send_message(message.channel, "Uh-oh! Retard alert! Retard alert, class!")
        asyncio.sleep(15)
        await self.send_message(message.channel,
                                mentions + ", do you really believe you're a " + fursona + ", bubblehead?!")
        asyncio.sleep(15)
        await self.send_message(message.channel, "Come on, you, you're going to have to sit in the dunce chair.")

    async def cmd_furfag(self, message, mention):
        try:
            await self.send_message(message.channel, "Oh look, looks like we have a retard.")
            await self.change_nickname(message.author, "Furfag")
            asyncio.sleep(1000)
            await self.send_typing(message.channel)
            await self.send_message(message.channel, "Idiot.")
            await self.change_nickname(message.author, message.author.name)
        except discord.errors.Forbidden:
            await self.send_message(message.channel,
                                    "```xl\n Whoops, there's an error.\n discord.errors.Forbidden: FORBIDDEN (status code: 403): Privilege is too low... \n Discord bot is forbidden to change the users nickname.\n```")

    async def cmd_nick(self, message, username, thingy):
        try:
            thingy = message.content[len(".nick " + username):].strip()
            await self.change_nickname(username, thingy)
            await self.send_message(message.channel, "Changed nickname of " + username + "to " + thingy)
        except discord.errors.Forbidden:
            await self.send_message(message.channel,
                                    "```xl\n Whoops, there's an error.\n discord.errors.Forbidden: FORBIDDEN (status code: 403): Privilege is too low... \n Discord bot is forbidden to change the users nickname.\n```")

    async def cmd_nickreset(self, message, username):
        try:
            await self.change_nickname(username, username)
            await self.send_message(message.channel, "Reset the nick name of " + username)
        except discord.errors.Forbidden:
            await self.send_message(message.channel,
                                    "```xl\n Whoops, there's an error.\n discord.errors.Forbidden: FORBIDDEN (status code: 403): Privilege is too low... \n Discord bot is forbidden to change the users nickname.\n```")

    async def cmd_github(self, message):
        await self.send_message(message.channel,
                                "https://github.com/RobinGall2910/RobTheBoat - Open source repos are fun.")
        await self.send_message(message.channel,
                                "https://travis-ci.org/robingall2910/RobTheBoat - Travis CI Build Status")

    @owner_only
    async def cmd_msgfags(self, message, id, reason):
        reason = message.content[len(".msgfags " + id):].strip()
        await self.send_message(discord.User(id=id), reason)
        await self.log(":information_source: Wyndrik sent a warning to ID #: `" + id + "`")

    async def cmd_kym(self, message):
        """
        Know your meme, {}kym
        """
        kym = message.content[len(".kym "):].strip()
        if message.content[len(".kym"):].strip() != 0:
            return Response("http://knowyourmeme.com/memes/" + re.sub(r"\s+", '-', kym) + "/", delete_after=0)
        elif message.content[len(".kym"):].strip() == 0:
            return Response("You didn't enter a message, or you didn't put in a meme.", delete_after=0)

    async def cmd_uploadfile(self, message):
        await self.send_file(message.channel, message.content[len(".uploadfile "):].strip())
        if FileNotFoundError == True:
            await self.send_message(message.channel, "There was no such thing found in the system.")

    async def cmd_python(self, message):
        await self.send_file(message.channel, "imgs/python.png")

    async def cmd_help(self):
        return Response("The help list is on here: https://dragonfire.me/robtheboat/info.html", delete_after=0)

    async def cmd_serverinv(self, message):
        await self.safe_send_message(message.channel, "Sent via a PM.")
        await self.safe_send_message(message.author,
                                     "https://discord.gg/0xyhWAU4n2ji9ACe - If you came for RTB help, ask for Some Dragon, not Music-Napsta. Or else people will implode.")

    async def cmd_date(self):
        return Response(
            "```xl\n Current Date: " + time.strftime("%A, %B %d, %Y") + '\n Current Time (Eastern): ' + time.strftime(
                "%I:%M:%S %p") + "\n" + "```", delete_after=0)

    async def cmd_talk(client, message):
        cb1 = cleverbot.Cleverbot()
        unsplit = message.content.split("talk")
        split = unsplit[1]
        answer = (cb1.ask(split))
        await client.send_message(message.channel, message.author.name + ": " + answer)

    async def cmd_test(self):
        return Response("( ͡° ͜ʖ ͡°) I love you", delete_after=0)

    async def cmd_kill(self, client, message, author):
        """
        Usage: .kill (person)
            Pretty self explanitory.
        """
        if message.content[len(".kill"):].strip() != message.author.mention:
            await self.safe_send_message(message.channel,
                                         "You've killed " + message.content[len(".kill "):].strip() + random.choice(
                                             suicidalmemes))
        elif message.content[len(".kill"):].strip() == "<@163698730866966528>":
            await self.safe_send_message(message.channel, "can u not im not gonna die")
        elif message.content[len(".kill"):].strip() == message.author.mention:
            await self.safe_send_message(message.channel,
                                         "<@" + message.author.id + ">" + " Nice one on your suicide. Just, it's so great.")

    async def cmd_say(self, client, message):
        """
        Usage: .say (faggot)
        """
        troyhasnodongs = message.content[len(".say "):].strip()
        return Response(troyhasnodongs.replace("@everyone", "everyone"), delete_after=0)

    async def cmd_donate(self, message):
        return Response(
            "`http://donate.dragonfire.me` - Here I guess. I can't keep up with the server, so I'm going to need all the help I can get. Thanks.")

    async def cmd_ship(self, client, message, content):
        """
        Usage: .ship (person) x (person)
        """
        if message.content[len(".ship "):].strip() == '<@163698730866966528> x <@163698730866966528>':
            return Response("I hereby ship, myself.... forever.... alone........ ;-;", delete_after=0)
        elif message.content[len(".ship "):].strip() == message.author.id == message.author.id:
            return Response("hah, loner", delete_after=0)
        elif message.content[len(".ship "):].strip() != '<@163698730866966528> x <@163698730866966528>':
            return Response("I hereby ship " + message.content[len(".ship"):].strip() + "!", delete_after=0)
            # todo: remove messages that wont make sense, like "no"

    async def cmd_nope(self):
        return Response("http://giphy.com/gifs/morning-good-reaction-ihWcaj6R061wc", delete_after=0)

    @owner_only
    async def cmd_rga(self):
        # Picks a random game thing from the list.
        whatever = random.choice(dis_games)
        discord.Game(Name=whatever)

        await self.change_status(whatever)

    @owner_only
    async def cmd_listservers(self, message):
        await self.send_message(message.channel, ", ".join([x.name for x in self.servers]))

    async def cmd_serverlookup(self, message):
        await self.send_message(message.channel, message.content[len(".serverlookup "):].strip() in self.servers)

    async def cmd_uptime(self):
        second = time.time() - st
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        week, day = divmod(day, 7)
        return Response(
            "I have been up for %d weeks," % (week) + " %d days," % (day) + " %d hours," % (hour) + " %d minutes," % (
            minute) + " and %d seconds." % (second), delete_after=0)

    async def cmd_createinv(self, message):
        invite = await self.create_invite(message.server)
        await self.send_message(message.channel, invite)

    @owner_only
    async def cmd_makeinvite(self, message):
        strippedk = message.content[len(".makeinvite "):].strip()
        inv2 = await self.create_invite(list(self.servers)[45])
        await self.send_message(message.channel,
                                "lol k here #" + message.content[len(".makeinvite "):].strip() + " " + inv2)

    async def cmd_stats(client, message):
        await client.send_message(message.channel,
                                  "```xl\n ~~~~~~RTB System Stats~~~~~\n Built by {}\n Bot Version: {}\n Build Date: {}\n Users: {}\n User Message Count: {}\n Servers: {}\n Channels: {}\n Private Channels: {}\n Discord Python Version: {}\n Status: ok \n Date: {}\n Time: {}\n ~~~~~~~~~~~~~~~~~~~~~~~~~~\n```".format(
                                      BUNAME, MVER, BUILD, len(set(client.get_all_members())),
                                      len(set(client.messages)), len(client.servers),
                                      len(set(client.get_all_channels())), len(set(client.private_channels)),
                                      discord.__version__, time.strftime("%A, %B %d, %Y"),
                                      time.strftime("%I:%M:%S %p")))

    """async def cmd_debug(self, message):
        if(message.content.startswith('.debug')):
            if message.author.id == '117678528220233731':
                debug = message.content[len(".debug "):].strip()
                try:
                    debug = eval(debug)
                    debug = str(debug)
                    await self.send_message(message.channel, "```python\n" + debug + "\n```")
                except Exception as e:
                    debug = traceback.format_exc()
                    debug = str(debug)
                    await self.send_message(message.channel, "```python\n" + debug + "\n```")
            else:
                pass"""

    async def cmd_debug(self, message):
        if (message.content.startswith('.debug ')):
            if message.author.id == '117678528220233731':
                debug = message.content[len(".debug "):].strip()
                py = "```py\n{}\n```"
                thing = None
                try:
                    thing = eval(debug)
                except Exception as e:
                    await self.send_message(message.channel, py.format(type(e).__name__ + ': ' + str(e)))
                    return
                if asyncio.iscoroutine(thing):
                    thing = await thing
                    await self.send_message(message.channel, py.format(thing))
            else:
                pass

    async def cmd_disconnect(self, server, message):
        await self.safe_send_message(message.channel, "Disconnected from the voice server.")
        await self.log(":mega: Disconnected from: `%s`" % server.name)
        await self.disconnect_voice_client(server)
        await self._manual_delete_check(message)

    async def cmd_reboot(self, message):
        # await self.safe_send_message(message.channel, "Bot is restarting, please wait...")
        await self.safe_send_message(message.channel, "brb")
        await self.log(":warning: Bot is restarting")
        await self.disconnect_all_voice_clients()
        raise exceptions.RestartSignal

    async def cmd_timetodie(self, message):
        await self.safe_send_message(message.channel, "Bot is shutting down...")
        await self.safe_send_message(message.channel, "btw BOT LIVES ***DO NOT*** MATTER.")
        await self.log(":warning: Bot is shutting down")
        await self.disconnect_all_voice_clients()
        raise exceptions.TerminateSignal

    async def on_message(self, message):
        if message.content == "BrAiNpOwEr https://www.youtube.com/watch?v=P6Z_s5MfDiA":
            await self.send_message(message.channel, "WHAT HAVE YOU DONE.")
        elif message.content == "<@!117678528220233731>, You aren't my owner 🚫" and message.author.bot == True:
            await self.send_message(message.channel, "Yes he is. Let him in, you bastard.")
        elif message.author.bot == True:
            return
        elif message.content == "O-oooooooooo AAAAE-A-A-I-A-U- JO-oooooooooooo AAE-O-A-A-U-U-A- E-eee-ee-eee AAAAE-A-E-I-E-A- JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA":
            await self.send_message(message.channel,
                                    "Ｏ－ｏｏｏｏｏｏｏｏｏｏ ＡＡＡＡＥ－Ａ－Ａ－Ｉ－Ａ－Ｕ－ ＪＯ－ｏｏｏｏｏｏｏｏｏｏｏｏ ＡＡＥ－Ｏ－Ａ－Ａ－Ｕ－Ｕ－Ａ－ Ｅ－ｅｅｅ－ｅｅ－ｅｅｅ ＡＡＡＡＥ－Ａ－Ｅ－Ｉ－Ｅ－Ａ－ ＪＯ－ｏｏｏ－ｏｏ－ｏｏ－ｏｏ ＥＥＥＥＯ－Ａ－ＡＡＡ－ＡＡＡＡ")
        await self.wait_until_ready()

        message_content = message.content.strip()
        if not message_content.startswith(self.config.command_prefix):
            return

        if message.author == self.user:
            self.safe_print("Ignoring command from myself (%s)" % message.content)
            return

        if self.config.bound_channels and message.channel.id not in self.config.bound_channels and not message.channel.is_private:
            return  # if I want to log this I just move it under the prefix check

        command, *args = message_content.split()  # Uh, doesn't this break prefixes with spaces in them (it doesn't, config parser already breaks them)
        command = command[len(self.config.command_prefix):].lower().strip()

        handler = getattr(self, 'cmd_%s' % command, None)
        if not handler:
            return

        if message.channel.is_private:
            if not (message.author.id == self.config.owner_id and command == 'joinserver'):
                await self.send_message(message.channel, 'You cannot use this bot in private messages.')
                return

        if message.author.id in self.blacklist and message.author.id != self.config.owner_id:
            self.safe_print("[User blacklisted] {0.id}/{0.name} ({1})".format(message.author, message_content))
            if self.config.log_interaction:
                await self.log(
                    ":no_pedestrians: `{0.name}#{0.discriminator}`: `{1}`".format(message.author, message_content),
                    message.channel)
            return

        elif self.config.white_list_check and int(
                message.author.id) not in self.whitelist and message.author.id != self.config.owner_id:
            self.safe_print("[User not whitelisted] {0.id}/{0.name} ({1})".format(message.author, message_content))
            if self.config.log_interaction:
                await self.log(
                    "Whitelisted: `{0.name}#{0.discriminator}`: `{1}`".format(message.author, message_content),
                    message.channel)
            return

        else:
            self.safe_print("[Command] {0.id}/{0.name} ({1})".format(message.author, message_content))

        user_permissions = self.permissions.for_user(message.author)

        argspec = inspect.signature(handler)
        params = argspec.parameters.copy()

        # noinspection PyBroadException
        try:
            if user_permissions.ignore_non_voice and command in user_permissions.ignore_non_voice:
                await self._check_ignore_non_voice(message)

            handler_kwargs = {}
            if params.pop('message', None):
                handler_kwargs['message'] = message

            if params.pop('channel', None):
                handler_kwargs['channel'] = message.channel

            if params.pop('author', None):
                handler_kwargs['author'] = message.author

            if params.pop('server', None):
                handler_kwargs['server'] = message.server

            if params.pop('player', None):
                handler_kwargs['player'] = await self.get_player(message.channel)

            if params.pop('permissions', None):
                handler_kwargs['permissions'] = user_permissions

            if params.pop('user_mentions', None):
                handler_kwargs['user_mentions'] = list(map(message.server.get_member, message.raw_mentions))

            if params.pop('channel_mentions', None):
                handler_kwargs['channel_mentions'] = list(map(message.server.get_channel, message.raw_channel_mentions))

            if params.pop('voice_channel', None):
                handler_kwargs['voice_channel'] = message.server.me.voice_channel

            if params.pop('leftover_args', None):
                handler_kwargs['leftover_args'] = args

            args_expected = []
            for key, param in list(params.items()):
                doc_key = '[%s=%s]' % (key, param.default) if param.default is not inspect.Parameter.empty else key
                args_expected.append(doc_key)

                if not args and param.default is not inspect.Parameter.empty:
                    params.pop(key)
                    continue

                if args:
                    arg_value = args.pop(0)
                    handler_kwargs[key] = arg_value
                    params.pop(key)

            if message.author.id != self.config.owner_id:
                if user_permissions.command_whitelist and command not in user_permissions.command_whitelist:
                    raise exceptions.PermissionsError(
                        "Command isn't enabled for: (%s)." % user_permissions.name,
                        expire_in=20)

                elif user_permissions.command_blacklist and command in user_permissions.command_blacklist:
                    raise exceptions.PermissionsError(
                        "This command is disabled for: (%s)." % user_permissions.name,
                        expire_in=20)

            if params:
                docs = getattr(handler, '__doc__', None)
                if not docs:
                    docs = 'Usage: {}{} {}'.format(
                        self.config.command_prefix,
                        command,
                        ' '.join(args_expected)
                    )

                docs = '\n'.join(l.strip() for l in docs.split('\n'))
                await self.safe_send_message(
                    message.channel,
                    '```\n%s\n```' % docs.format(command_prefix=self.config.command_prefix),
                    expire_in=60
                )
                return

            response = await handler(**handler_kwargs)
            if response and isinstance(response, Response):
                content = response.content
                if response.reply:
                    content = '%s, %s' % (message.author.mention, content)

                sentmsg = await self.safe_send_message(
                    message.channel, content,
                    expire_in=response.delete_after if self.config.delete_messages else 0,
                    also_delete=message if self.config.delete_invoking else None
                )

        except (exceptions.CommandError, exceptions.HelpfulError, exceptions.ExtractionError) as e:
            print("{0.__class__}: {0.message}".format(e))
            await self.safe_send_message(message.channel, '```\n%s\n```' % e.message, expire_in=e.expire_in)

        except exceptions.Signal:
            raise

        except Exception:
            traceback.print_exc()
            if self.config.log_exceptions:
                await self.log(":warning: `%s#%s` encountered an Exception:\n```python\n%s\n```" % (
                self.user.name, self.user.discriminator, traceback.format_exc()), message.channel)

    async def on_server_join(self, server):
        if self.config.log_interaction:
            await self.log(
                ":performing_arts: `%s#%s` joined: `%s`" % (self.user.name, self.user.discriminator, server.name))

    async def on_server_remove(self, server):
        if self.config.log_interaction:
            await self.log(
                ":performing_arts: `%s#%s` left: `%s`" % (self.user.name, self.user.discriminator, server.name))

    async def on_server_update(self, before: discord.Server, after: discord.Server):
        if before.region != after.region:
            self.safe_print("[Servers] \"%s\" changed regions: %s -> %s" % (after.name, before.region, after.region))
        if self.config.log_interaction:
            await self.log(":house: `{}` changed regions: `{}` to `{}`".format(after.name, before.region, after.region))

        await self.reconnect_voice_client(after)

    async def on_voice_state_update(self, before, after):
        if not all([before, after]):
            return

        if before.server.id not in self.players:
            return

        my_voice_channel = after.server.me.voice_channel  # This should always work, right?

        auto_paused = self.server_specific_data[after.server]['auto_paused']
        player = await self.get_player(my_voice_channel)

        if after == after.server.me and after.voice_channel:
            player.voice_client.channel = after.voice_channel

        if not self.config.auto_pause:
            return

        num_deaf = sum(1 for m in my_voice_channel.voice_members if (
            m.deaf or m.self_deaf))

        if (len(my_voice_channel.voice_members) - 1) != num_deaf:
            if auto_paused and player.is_paused:
                print("[config:autopause] Unpausing")
                self.server_specific_data[after.server]['auto_paused'] = False
                player.resume()
        else:
            if not auto_paused and player.is_playing:
                print("[config:autopause] Pausing")
                self.server_specific_data[after.server]['auto_paused'] = True
                player.pause()

        if before.voice_channel == after.voice_channel:
            return

        if not my_voice_channel:
            return

        if not my_voice_channel:
            return

        if before.voice_channel == my_voice_channel:
            joining = False
        elif after.voice_channel == my_voice_channel:
            joining = True
        else:
            return  # Not my channel

        moving = before == before.server.me

        if sum(1 for m in my_voice_channel.voice_members if m != after.server.me):
            if auto_paused and player.is_paused:
                print("[config:autopause] Unpausing")
                self.server_specific_data[after.server]['auto_paused'] = False
                player.resume()
        else:
            if not auto_paused and player.is_playing:
                print("[config:autopause] Pausing")
                self.server_specific_data[after.server]['auto_paused'] = True
                player.pause()


if __name__ == '__main__':
    bot = RTB()
    bot.run()
