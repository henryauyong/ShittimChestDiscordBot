import datetime
from discord.ext import commands, tasks
from pathlib import Path
from .utils import get_data_global
from .utils import get_data_japan

pwd = Path(__file__).parent
utc = datetime.timezone.utc
time = datetime.time(hour=7, minute=0, second=0, tzinfo=utc)

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update.start()

    def cog_unload(self):
        self.update.cancel()

    @tasks.loop(time=time)
    async def update(self):
        await self.bot.reload_extension('cogs.gacha')
        get_data_global.update()
        get_data_japan.update()
        print(f"Updated at {datetime.datetime.now(utc)}")
    
async def setup(bot):
    await bot.add_cog(Update(bot))