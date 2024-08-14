from discord.ext import commands
from .utils import get_data_global
from .utils import get_data_japan
from .utils import get_raid_global
from .utils import raid_db
from pathlib import Path
import discord

pwd = Path(__file__).parent

with open((pwd/"../config/admin_roles.txt").as_posix(), "r", encoding="utf-8") as f:
    ADMIN_ROLES = f.read().splitlines()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="reload", description="重新載入指令")
    async def reload(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                await self.bot.reload_extension('cogs.admin')
                await self.bot.reload_extension('cogs.gacha')
                await self.bot.reload_extension('cogs.update')
                await self.bot.reload_extension('cogs.rps')
                await self.bot.reload_extension('cogs.raid')
                await ctx.send("Reloaded all commands")
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="update", description="手動更新資料庫")
    async def update(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                get_data_global.update()
                get_data_japan.update()
                await self.bot.reload_extension('cogs.gacha')
                await ctx.send("Updated database manually")
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="sync", description="")
    async def sync(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                self.bot.tree.clear_commands(guild=discord.Object(id=863849091821994014))
                self.bot.tree.copy_global_to(guild=discord.Object(id=863849091821994014))
                synced = await self.bot.tree.sync(guild=discord.Object(id=863849091821994014))
                await ctx.send(f"{len(synced)} Commands synced")
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="sync-global", description="同步全域指令")
    async def sync_global(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                synced = await self.bot.tree.sync()
                await ctx.send(f"{len(synced)} Commands synced")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command(name="resetglta", description="")
    async def resetglta(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_data("global", "raid")
                await ctx.send("Reset global raid data")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command(name="resetglga", description="")
    async def resetglga(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_data("global", "eliminate_raid")
                await ctx.send("Reset global eliminate raid data")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command(name="resetjpta", description="")
    async def resetjpta(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_data("japan", "raid")
                await ctx.send("Reset japan raid data")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command(name="resetjpga", description="")
    async def resetjpga(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_data("japan", "eliminate_raid")
                await ctx.send("Reset japan eliminate raid data")
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="resetgltaet", description="")
    async def resetgltet(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_excel_table("global", "raid")
                await ctx.send("Reset global raid excel table")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command(name="resetglgaet", description="")
    async def resetglet(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_excel_table("global", "eliminate_raid")
                await ctx.send("Reset global eliminate raid excel table")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command(name="resetjptaet", description="")
    async def resetjptet(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_excel_table("japan", "raid")
                await ctx.send("Reset japan raid excel table")
        except Exception as e:
            await ctx.send(e)
    
    @commands.command(name="resetjpgaet", description="")
    async def resetjpet(self, ctx:commands.Context):
        try:
            if [i for i in ctx.author.roles if i.name in ADMIN_ROLES]:
                raid_db.delete_excel_table("japan", "eliminate_raid")
                await ctx.send("Reset japan eliminate raid excel table")
        except Exception as e:
            await ctx.send(e)
        
async def setup(bot):
    await bot.add_cog(Admin(bot))