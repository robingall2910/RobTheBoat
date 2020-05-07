"""Chatlog

This module records the chat messages in the SQLite database.
"""


import re
import string

import discord
from discord.ext import commands

from utils.mysql import addword

class ChatLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.valid or message.author.bot:
            return
        else:
            record = self.clean_message(message.clean_content)
            if record:
                record.split()
                for x in record:
                    addword(x, message.author.guild.id, message.author.id)

    def clean_message(self, message):
        """Cleans the message of unnecessary information.

        Args:
            message (str): Message from the chat to modify.

        Returns:
            text (str): Text that has URLs, mentions, and punctuation removed.
        """
        text = message.lower()
        text = text.replace('codex', '')
        text = re.sub(r'''(\s)\#\w+''', '', text)
        text = re.sub(
            r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'''
            r'''(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'''
            r'''(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|'''
            r'''[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', '', text
        )
        depunctuate = str.maketrans('', '', string.punctuation)
        text = text.translate(depunctuate)
        text = ' '.join(text.split())
        return text


def setup(bot):
    bot.add_cog(ChatLog(bot))
