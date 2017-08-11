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
            channel = self.bot.get_channel(int(config.channel_logger_id))
            if not channel:
                log.warning("Can't find logging channel")
            else:
                try:
                    await channel.send(":stopwatch: `{}` {}".format(time.strftime(config.log_timeformat), msg))
                except discord.errors.Forbidden:
                    log.warning("Could not log to the channel log channel because I do not have permission to send messages in it!")