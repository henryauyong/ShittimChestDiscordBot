from discord.ext import commands
import discord

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="reload", description="Reload commands")
    async def reload(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name == "test"]:
                await self.bot.reload_extension('cogs.admin')
                await self.bot.reload_extension('cogs.sync')
                await self.bot.reload_extension('cogs.gacha')
                await ctx.send("Reloaded")
        except Exception as e:
            await ctx.send(e)
        
async def setup(bot):
    await bot.add_cog(Admin(bot))