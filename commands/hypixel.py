import itertools
import json
import sys
import time
import traceback
import urllib

import hypixel
import asyncio

from discord.ext import commands
from utils.config import Config
from utils.logger import log
from utils import checks
from utils.tools import *

config = Config()

key = [config._hypixelKey] #no push perms anyway, & not my api key
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
            cflogin = datetime.fromtimestamp(flogin/1000.0).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')
            if ctx.me.color is not None:
                embed.color = ctx.me.color
            try:
                ltu = hypixel.Player(player.JSON['mostRecentlyTippedUuid']).getName()  #deprecated? constantly doesn't work
            except KeyError:
                ltu = "They haven't tipped anyone recently."
            try:
                guildname = hypixel.Guild(player.getGuildID()).JSON['name']
            except Exception: #shut up code convention i dont care
                guildname = "They aren't in a gang."
            try:
                lmv = player.JSON['mcVersionRp'] #deprecated? constantly doesn't work
            except KeyError:
                lmv = "They haven't played Minecraft in years, I guess."
            try:
                llogin = player.JSON['lastLogin']
                cllogin = datetime.fromtimestamp(llogin / 1000.0).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')
            except KeyError:
                cllogin = "They hid their last login. Figure it out yourself."
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
            if sys.platform == "windows":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            elif sys.platform == "linux":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        except hypixel.PlayerNotFoundException:
            await ctx.send("Player not found! Try another UUID or username.")
        except Exception:
            await ctx.send(traceback.print_exc())

    @commands.command(aliases=['ginfo', 'hginfo', 'hg'])
    async def hguildinfo(self, ctx, *, dirtygname: str):
        try:
            gname = dirtygname.replace(" ", "%20")
            link = f"https://api.hypixel.net/findGuild?key={config._hypixelKey}&byName={gname}" #raw key
            r = requests.get(link)
            gid = r.json()['guild']
            guild = hypixel.Guild(gid)
            playercount = len(guild.JSON['members'])
            def t5exp():
                try:
                    explist = []
                    todaysdate = str(datetime.now().date().isoformat())
                    if 5 <= len(guild.JSON['members']):
                        smallerone = len(guild.JSON['members'])
                    else:
                        smallerone = 5
                    for w in range(0, len(guild.JSON['members'])):
                        try:
                            if guild.JSON['members'][w]['expHistory'][todaysdate] == 0:
                                continue
                            else:
                                ass = guild.JSON['members'][w]['expHistory'][todaysdate]
                                print("gay" + str(ass))
                                ass2 = guild.JSON['members'][w]['uuid']
                                print("h" + str(ass2))
                                ass3 = [ass, ass2]
                                explist.append(ass3)
                                print("y" + str(ass3))
                        except KeyError:
                            continue 
                    print("unsorted" + str(explist))        
                    explist.sort(key=lambda x: x[1], reverse = True)
                    print("sorted" + str(explist))
                    top5 = list(itertools.islice(explist, smallerone))
                    print("final" + str(top5))
                    if len(guild.JSON['members']) == 4:
                        return f"#1 - {top5[0][0]}{top5[0][1]}\n#2 - {top5[1][0]}{top5[1][1]}\n#3 - {top5[2][0]}{top5[2][1]}\n#4 - {top5[3][0]}{top5[3][1]}"
                    if len(guild.JSON['members']) == 3:
                        return f"#1 - {top5[0][0]}{top5[0][1]}\n#2 - {top5[1][0]}{top5[1][1]}\n#3 - {top5[2][0]}{top5[2][1]}"
                    if len(guild.JSON['members']) == 2:
                        return f"#1 - {top5[0][0]}{top5[0][1]}\n#2 - {top5[1][0]}{top5[1][1]}"
                    if len(guild.JSON['members']) == 1:
                        return f"The only one - {top5[0][0]}"
                    else:
                        return f"#1 - {top5[0][0]}{top5[0][1]}\n#2 - {top5[1][0]}{top5[1][1]}\n#3 - {top5[2][0]}{top5[2][1]}\n#4 - {top5[3][0]}{top5[3][1]}\n#5 - {top5[4][0]}{top5[4][1]}"
                except Exception:
                    traceback.print_exc()
            try:
                embed = discord.Embed(description=f"{guild.JSON['description']}")
            except KeyError:
                embed = discord.Embed()
            try:
                embed.title = f"[{guild.JSON['tag']}] - {guild.JSON['name']} ({playercount} members)"
            except KeyError:
                embed.title = f"{guild.JSON['name']} - ({playercount} members)"
            if guild.JSON['tagColor'] == 'YELLOW':
                embed.color = 0xfff70d
            if guild.JSON['tagColor'] == 'DARK_GREEN':
                embed.color = 0x008a15
            if guild.JSON['tagColor'] == 'DARK_AQUA':
                embed.color = 0x0cb0c2
            if guild.JSON['tagColor'] == 'GOLD':
                embed.color = 0xe3ca0e
            else: # gray
                embed.color = 0xadadad
            embed.add_field(name='Created', value=f"{datetime.fromtimestamp(guild.JSON['created'] / 1000.0).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')}")
            embed.add_field(name='Coins', value=f"{guild.JSON['coins']}")
            embed.add_field(name='Experience', value=f"{guild.JSON['exp']}")
            embed.add_field(name='Top 5 Gained Exp', value=t5exp())
            try:
                for s in range(0, len(guild.JSON['preferredGames'])):
                    #except that arrays start at one @kurt
                    embed.add_field(name=f'Preferred Games #{s}', value=f"{guild.JSON['preferredGames'][s]}")
            except KeyError:
                pass
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send(traceback.format_exc())
                                    
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
            if sys.platform == "windows":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            elif sys.platform == "linux":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        except hypixel.PlayerNotFoundException:
            await ctx.send("Player not found! Try another UUID or username.")
        except KeyError:
            await ctx.send("This user has never played Bed Wars before.")
        except Exception:
            await ctx.send(traceback.print_exc())

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
            if sys.platform == "windows":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            elif sys.platform == "linux":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        except hypixel.PlayerNotFoundException:
            await ctx.send("Player not found! Try another UUID or username.")
        except KeyError:
            await ctx.send("This user has never played Skywars before.")
        except Exception:
            await ctx.send(traceback.print_exc())

    @commands.command(aliases=['playercount'])
    async def hpc(self, ctx):
        try:
            pc = hypixel.getJSON('playercount')['playerCount']
            embed = discord.Embed(description=f"Total people online - {pc} players")
            embed.title = "Hypixel Player Count"
            if ctx.me.color is not None:
                embed.color = ctx.me.color
            embed.add_field(name="Skyblock", value=f"{hypixel.getJSON('gameCounts')['games']['SKYBLOCK']['players']}")
            embed.add_field(name="Bed Wars", value=f"{hypixel.getJSON('gameCounts')['games']['BEDWARS']['players']}")
            embed.add_field(name="AFK", value=f"{hypixel.getJSON('gameCounts')['games']['IDLE']['players']}")
            embed.add_field(name="Skywars", value=f"{hypixel.getJSON('gameCounts')['games']['SKYWARS']['players']}")
            embed.add_field(name="Housing", value=f"{hypixel.getJSON('gameCounts')['games']['HOUSING']['players']}")
            embed.add_field(name="Duels", value=f"{hypixel.getJSON('gameCounts')['games']['DUELS']['players']}")
            embed.add_field(name="Arcade Games", value=f"{hypixel.getJSON('gameCounts')['games']['ARCADE']['players']}")
            embed.add_field(name="Murder Mystery", value=f"{hypixel.getJSON('gameCounts')['games']['MURDER_MYSTERY']['players']}")
            embed.add_field(name="Build Battle", value=f"{hypixel.getJSON('gameCounts')['games']['BUILD_BATTLE']['players']}")
            embed.add_field(name="The Pit", value=f"{hypixel.getJSON('gameCounts')['games']['PIT']['players']}")
            embed.add_field(name="Prototype Games", value=f"{hypixel.getJSON('gameCounts')['games']['PROTOTYPE']['players']}")
            embed.add_field(name="TNT Games", value=f"{hypixel.getJSON('gameCounts')['games']['TNTGAMES']['players']}")
            embed.add_field(name="UHC", value=f"{hypixel.getJSON('gameCounts')['games']['UHC']['players']}")
            embed.add_field(name="Classic Games", value=f"{hypixel.getJSON('gameCounts')['games']['LEGACY']['players']}")
            embed.add_field(name="Mega Walls", value=f"{hypixel.getJSON('gameCounts')['games']['WALLS3']['players']}")
            embed.add_field(name="Main Lobby", value=f"{hypixel.getJSON('gameCounts')['games']['MAIN_LOBBY']['players']}")
            embed.add_field(name="Survival Games", value=f"{hypixel.getJSON('gameCounts')['games']['SURVIVAL_GAMES']['players']}")
            embed.add_field(name="Stuck in Limbo", value=f"{hypixel.getJSON('gameCounts')['games']['LIMBO']['players']}")
            embed.add_field(name="Cops and Crims", value=f"{hypixel.getJSON('gameCounts')['games']['MCGO']['players']}")
            embed.add_field(name="Warlords", value=f"{hypixel.getJSON('gameCounts')['games']['BATTLEGROUND']['players']}")
            embed.add_field(name="Super Smash™", value=f"{hypixel.getJSON('gameCounts')['games']['SUPER_SMASH']['players']}")
            embed.add_field(name="Speed UHC", value=f"{hypixel.getJSON('gameCounts')['games']['SPEED_UHC']['players']}")
            embed.add_field(name="Crazy Walls", value=f"{hypixel.getJSON('gameCounts')['games']['TRUE_COMBAT']['players']}")
            embed.add_field(name="Turbo Kart Racer", value=f"{hypixel.getJSON('gameCounts')['games']['LEGACY']['modes']['GINGERBREAD']}")
            if sys.platform == "windows":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            elif sys.platform == "linux":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send(traceback.print_exc())

    @commands.command(aliases=['duelsinfo', 'dinfo', 'hdinfo'])
    async def hduels(self, ctx, username: str):
        try:
            player = hypixel.Player(username)
            embed = discord.Embed(description=f"They've played {player.JSON['stats']['Duels']['games_played_duels']} times.")
            embed.title = f"{username}'s Duels Stats"
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{player.UUID}?size=64")
            embed.add_field(name="Coins", value=f"{player.JSON['stats']['Duels']['coins']}")
            embed.add_field(name="Wins", value=f"{player.JSON['stats']['Duels']['wins']}")
            embed.add_field(name="Losses", value=f"{player.JSON['stats']['Duels']['losses']}")
            embed.add_field(name="Deaths", value=f"{player.JSON['stats']['Duels']['deaths']}")
            try:
                embed.add_field(name="Kills", value=f"{player.JSON['stats']['Duels']['kills']}")
            except KeyError:
                embed.add_field(name="Kills", value="0")
            try:
                embed.add_field(name="Cosmetic Title", value=f"{player.JSON['stats']['Duels']['active_cosmetictitle']}")
            except KeyError:
                pass
            embed.add_field(name="Goals Hit", value=f"{player.JSON['stats']['Duels']['goals']} times")
            embed.add_field(name="Bow Shots", value=f"{player.JSON['stats']['Duels']['bow_shots']}")
            embed.add_field(name="Bow Hits", value=f"{player.JSON['stats']['Duels']['bow_hits']}")
            wdr = int(player.JSON['stats']['Duels']['wins'])/int(player.JSON['stats']['Duels']['losses'])
            try:
                kdr = int(player.JSON['stats']['Duels']['kills'])/int(player.JSON['stats']['Duels']['deaths'])
            except KeyError:
                kdr = int(0/int(player.JSON['stats']['Duels']['deaths']))
            awdr = '{:,.2f}'.format(wdr)
            akdr = '{:,.2f}'.format(kdr)
            if akdr == "0.00":
                akdr = "0"
            else:
                pass
            embed.add_field(name='Win/Loss Ratio', value=f"{awdr}")
            embed.add_field(name='Kill/Death Ratio', value=f"{akdr}")
            if sys.platform == "windows":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %#d, %Y at %#I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            elif sys.platform == "linux":
                embed.set_footer(
                    text=f"Requested by: {ctx.message.author} / {datetime.fromtimestamp(time.time()).strftime('%A, %B %-d, %Y at %-I:%M %p %Z')}",
                    icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        except hypixel.PlayerNotFoundException:
            await ctx.send("Player not found! Try another UUID or username.")
        except KeyError:
            await ctx.send("This user has never played Duels (of any kind) before.")
        except Exception:
            await ctx.send(traceback.print_exc())

    @commands.command()
    @checks.is_dev()
    async def hdebug(self, ctx, *, shit: str):
        try:
            player = hypixel.Player("Premintex")
            guild = hypixel.Guild("5a8058500cf2252f5fc3ceb0")
            rebug = eval(shit)
            if asyncio.iscoroutine(rebug):
                rebug = await rebug
            else:
                await ctx.send(py.format(rebug))
        except Exception as damnit:
            await ctx.send(py.format("{}: {}".format(type(damnit).__name__, damnit)))
def setup(bot):
    bot.add_cog(Hypixel(bot))



