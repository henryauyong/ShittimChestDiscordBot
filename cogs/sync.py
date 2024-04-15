from discord.ext import commands
import discord

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sync", description="Sync commands")
    async def sync(self, ctx:commands.Context):
        try:
            self.bot.tree.clear_commands(guild=discord.Object(id=863849091821994014))
            self.bot.tree.copy_global_to(guild=discord.Object(id=863849091821994014))
            synced = await self.bot.tree.sync(guild=discord.Object(id=863849091821994014))
            await ctx.send(f"{len(synced)} Commands synced")
        except Exception as e:
            await ctx.send(e)

async def setup(bot):
    await bot.add_cog(Sync(bot))