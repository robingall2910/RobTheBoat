import traceback

import discord
import hypixel
import asyncio

from discord.ext import commands
from utils.config import Config
from utils.logger import log
from utils import checks
from utils.tools import *

config = Config()

key = [config._hypixelKey]
hypixel.setKeys(key)

class Hypixel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["hinfo"])
    async def hypixelinfo(self, ctx, username: str):
        try:
            player = hypixel.Player(username)
            embed = discord.Embed(description=None)
            flogin = player.JSON['firstLogin']
            llogin = player.JSON['lastLogin']
            cflogin = datetime.fromtimestamp(flogin/1000.0).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')
            cllogin = datetime.fromtimestamp(llogin/1000.0).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')
            if ctx.me.color is not None:
                embed.color = ctx.me.color
            try:
                ltu = hypixel.Player(player.JSON['mostRecentlyTippedUuid']).getName()
            except KeyError:
                ltu = "They haven't tipped anyone recently."
            try:
                guildname = hypixel.Guild(player.getGuildID()).JSON['name']
            except Exception: #shut up code convention i dont care
                guildname = "They aren't in a gang."
            try:
                lmv = player.JSON['mcVersionRp']
            except KeyError:
                lmv = "They haven't played Minecraft in years, I guess."
            plevel = player.getLevel()
            cplevel = '{:,.0f}'.format(plevel)
            embed.title = f"{player.getName()}'s Hypixel Stats"
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{player.UUID}?size=64")
            embed.add_field(name="Rank", value=f"{player.getRank()['rank']}")
            embed.add_field(name="Level", value=f"{cplevel}")
            embed.add_field(name="Guild Name", value=f"{guildname}")
            embed.add_field(name="First Login", value=f"{cflogin}")
            embed.add_field(name="Last Login", value=f"{cllogin}")
            embed.add_field(name="Last Minecraft Version played", value=f"{lmv}")
            embed.add_field(name="Last Tipped User", value=f"{ltu}")
            await ctx.send(embed=embed)
        except hypixel.PlayerNotFoundException:
            await ctx.send("Player not found! Try another UUID or username.")
        except Exception:
            traceback.print_exc()

    @commands.command(aliases=['bedwars', 'binfo', 'bwinfo'])
    async def hbedwars(self, ctx, username: str):
        try:
            player = hypixel.Player(username)
            embed = discord.Embed(description=f"Level {player.JSON['achievements']['bedwars_level']}")
            embed.title = f"{player.getName()}'s Bedwars Stats"
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{player.UUID}?size=64")
            if ctx.me.color is not None:
                embed.color = ctx.me.color
            try:
                embed.add_field(name='Beds Broken', value="{:,}".format(player.JSON['achievements']['bedwars_beds']))
            except KeyError:
                embed.add_field(name='Beds Broken', value="None. They're innocent, your honor.")
            embed.add_field(name='Coins', value=f"{player.JSON['stats']['Bedwars']['coins']}")
            embed.add_field(name='Winstreak', value=f"{player.JSON['stats']['Bedwars']['winstreak']}")
            embed.add_field(name='Wins', value="{:,}".format(player.JSON['achievements']['bedwars_wins']))
            embed.add_field(name='Losses', value="{:,}".format(player.JSON['stats']['Bedwars']['losses_bedwars']))
            embed.add_field(name='Kills', value=f"{player.JSON['stats']['Bedwars']['kills_bedwars']}")
            embed.add_field(name='Final Kills', value=f"{player.JSON['stats']['Bedwars']['final_kills_bedwars']}")
            embed.add_field(name='Deaths', value=f"{player.JSON['stats']['Bedwars']['deaths_bedwars']}")
            embed.add_field(name='Final Deaths', value=f"{player.JSON['stats']['Bedwars']['final_deaths_bedwars']}")
            embed.add_field(name='Emeralds collected',
                            value=f"{player.JSON['stats']['Bedwars']['emerald_resources_collected_bedwars']}")
            embed.add_field(name='Diamonds collected',
                            value=f"{player.JSON['stats']['Bedwars']['diamond_resources_collected_bedwars']}")
            embed.add_field(name='Gold collected',
                            value=f"{player.JSON['stats']['Bedwars']['gold_resources_collected_bedwars']}")
            embed.add_field(name='Iron collected',
                            value=f"{player.JSON['stats']['Bedwars']['iron_resources_collected_bedwars']}")
            wdr = int(player.JSON['achievements']['bedwars_wins'])/int(player.JSON['stats']['Bedwars']['losses_bedwars'])
            kdr = int(player.JSON['stats']['Bedwars']['kills_bedwars'])/int(player.JSON['stats']['Bedwars']['deaths_bedwars'])
            fkdr = int(player.JSON['stats']['Bedwars']['final_kills_bedwars']) / int(player.JSON['stats']['Bedwars']['final_deaths_bedwars'])
            awdr = '{:,.2f}'.format(wdr)
            akdr = '{:,.2f}'.format(kdr)
            afkdr = '{:,.2f}'.format(fkdr)
            embed.add_field(name='Win/Loss Ratio', value=f"{awdr}")
            embed.add_field(name='Kill/Death Ratio', value=f"{akdr}")
            embed.add_field(name='Final Kill/Final Death Ratio', value=f"{afkdr}")
            await ctx.send(embed=embed)
        except Exception:
            traceback.print_exc()

    @commands.command(aliases=['skywars', 'sinfo', 'swinfo'])
    async def hskywars(self, ctx, username: str):
        try:
            player = hypixel.Player(username)
            embed = discord.Embed(description=None)
            embed.title = f"{player.getName()}'s Skywars Stats"
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{player.UUID}?size=64")
            if ctx.me.color is not None:
                embed.color = ctx.me.color
            embed.add_field(name="Coins",
                            value=f"{player.JSON['stats']['SkyWars']['coins']}")
            embed.add_field(name="Kills (Solo)", value=f"{player.JSON['achievements']['skywars_kills_solo']}")
            embed.add_field(name="Kills (Teams)",
                            value=f"{player.JSON['achievements']['skywars_kills_team']}")
            embed.add_field(name="Wins (Solo)",
                            value=f"{player.JSON['achievements']['skywars_wins_solo']}")
            embed.add_field(name="Wins (Teams)",
                            value=f"{player.JSON['achievements']['skywars_wins_team']}")
            embed.add_field(name="Kills (Solo)",
                            value=f"{player.JSON['achievements']['skywars_kills_solo']}")
            embed.add_field(name="Deaths",
                            value=f"{player.JSON['stats']['SkyWars']['deaths']}")
            embed.add_field(name="Games Played",
                            value=f"{player.JSON['stats']['SkyWars']['games']}")
            try:
                embed.add_field(name="Lucky Blocks Wins", value=f"{player.JSON['stats']['SkyWars']['lab_win_lucky_blocks_lab']}")
            except KeyError:
                embed.add_field(name="Lucky Blowck Wins", value="They have not won in LUCKY BLOWCKS")
            wdr = (int(player.JSON['achievements']['skywars_wins_solo'])+int(player.JSON['achievements']['skywars_wins_team']))/(int(player.JSON['stats']['SkyWars']['deaths']))
            kdr = (int(player.JSON['achievements']['skywars_kills_solo'])+int(player.JSON['achievements']['skywars_kills_team']))/(int(player.JSON['stats']['SkyWars']['deaths']))
            awdr = '{:,.2f}'.format(wdr)
            akdr = '{:,.2f}'.format(kdr)
            embed.add_field(name='Win/Loss Ratio (Overall)', value=f"{awdr}")
            embed.add_field(name='Kill/Death Ratio (Overall)', value=f"{akdr}")
            await ctx.send(embed=embed)
        except Exception:
            traceback.print_exc()

    #TODO: Check skywars command
    #TODO: Duels/Bridge command

    @commands.command()
    @checks.is_dev()
    async def hdebug(self, ctx, *, shit: str):
        try:
            player = hypixel.Player("hardnt")
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            else:
                await ctx.send(py.format(rebug))
        except Exception as damnit:
            await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))
def setup(bot):
    bot.add_cog(Hypixel(bot))



