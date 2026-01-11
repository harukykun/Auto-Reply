import discord
from discord.ext import commands
class Camping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def camping(self, ctx):
        USER_ID_ALLOWED = 960541228422815824
        if ctx.author.id == USER_ID_ALLOWED:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                if ctx.voice_client:
                    await ctx.voice_client.move_to(channel)
                else:
                    await channel.connect()
    @commands.command()
    async def outcamp(self, ctx):
        USER_ID_ALLOWED = 960541228422815824
        if ctx.author.id == USER_ID_ALLOWED:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
async def setup(bot):
    await bot.add_cog(Camping(bot))