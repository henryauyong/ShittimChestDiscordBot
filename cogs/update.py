import datetime
from discord.ext import commands, tasks
from pathlib import Path
from .utils import get_data_global
from .utils import get_data_japan
from .utils import get_raid_global
from datetime import timedelta
import pytz

pwd = Path(__file__).parent
timezone = pytz.timezone('Asia/Taipei')

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_gacha(self):
        get_data_global.update()
        get_data_japan.update()
        await self.bot.reload_extension('cogs.gacha')
        print(f"Updated gacha data at {datetime.datetime.now(timezone)}")
    
async def setup(bot):
    await bot.add_cog(Update(bot))