from discord.ext import commands

class RWBY():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rwby(self):
        """Gives you the link to watch RWBY"""
        await self.bot.say("You can watch RWBY here fam: http://roosterteeth.com/show/rwby")

    @commands.command(pass_context=True)
    async def scream(self, ctx):
        """AAAAAAAAAAAAAAAAAAAA"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/scream.jpg")

    @commands.command(pass_context=True)
    async def what(self, ctx):
        """What?"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_file(ctx.message.channel, "assets/imgs/what.gif")


def setup(bot):
    bot.add_cog(RWBY(bot))
