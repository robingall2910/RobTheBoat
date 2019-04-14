import discord
import tweepy


from discord.ext import commands
from utils.config import Config
from utils.logger import log

config = Config()

auth = tweepy.OAuthHandler(config._twitterConsumerKey, config._twitterConsumerSecret)
auth.set_access_token(config._twitterAccessToken, config._twitterAccessTokenSecret)

api = tweepy.API(auth)

# Get the User object for twitter...
user = api.get_user('robinsmeme')

log.info(f"[Twitter] Logged in as {user.screen_name}")

class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Twitter(bot))