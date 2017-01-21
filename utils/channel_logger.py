import discord
import time

from utils.logger import log
from utils.config import Config
config = Config()

class Channel_Logger():
    def __init__(self, bot):
        self.bot = bot

    async def log_to_channel(self, msg):
        if config.channel_logger_id:
            channel = self.bot.get_channel(config.channel_logger_id)
            if not channel:
                log.warning("Can't find logging master channel: {}".format(id))
            else:
                try:
                    await self.bot.send_message(channel, ":stopwatch: `{}` :mouse_three_button: `{}` {}".format(time.strftime(config.log_timeformat), channel.server.name, msg))
                except discord.errors.Forbidden:
                    log.warning("Could not log to the channel log channel because I do not have permission to send messages in it!")

    async def mod_log(self, server, msg):
        log_channel = discord.utils.get(server.channels, name="mod-log")
        if log_channel:
            try:
                await self.bot.send_message(log_channel, ":information_source: Moderator action: {}".format(msg))
            except:
                pass
