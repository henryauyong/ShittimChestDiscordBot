from discord.ext import commands
import discord
import json
from discord import app_commands
from pathlib import Path
import datetime
import pytz

pwd = Path(__file__).parent

timezone = pytz.timezone('Asia/Taipei')
translate = {}
global_current_raid = {}
image_link = {}
with open((pwd/"../raid_data/global/current_raid.json").as_posix(), "r", encoding="utf-8") as f:
    global_current_raid = json.load(f)
with open((pwd/"../raid_data/global/translate.json").as_posix(), "r", encoding="utf-8") as f:
    translate = json.load(f)
with open((pwd/"../raid_data/image.json").as_posix(), "r", encoding="utf-8") as f:
    image_link = json.load(f)
if global_current_raid:
    global_type = global_current_raid["Type"]
    global_season = global_current_raid["Season"]
    global_name = global_current_raid["Name"]
    global_update_time = global_current_raid["UpdateTime"]

class RaidLineEmbed(discord.Embed):
    def __init__(self, server: str):
        if server == "國際服":
            type = global_type
            season = global_season
            name = global_name
            update_time = global_update_time
            current_raid = global_current_raid
        super().__init__(title=f'{server} 第{season}期{type} {translate[name]}', color=discord.Color.blue())
        self.set_thumbnail(url=image_link[name])
        self.add_field(name=f'一檔第一名：{current_raid["Platinum"]["Name"]}', value=f'{current_raid["Platinum"]["Score"]}', inline=False)
        self.add_field(name=f'二檔第一名：{current_raid["Gold"]["Name"]}', value=f'{current_raid["Gold"]["Score"]}', inline=False)
        self.add_field(name=f'三檔第一名：{current_raid["Silver"]["Name"]}', value=f'{current_raid["Silver"]["Score"]}', inline=False)
        self.set_footer(text=f'資料更新時間：{update_time}')

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='raid-line', description='查看當期總力戰/大決戰檔線')
    async def raid(self, interaction: discord.Interaction):
        if global_current_raid:
            embed = RaidLineEmbed("國際服")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="目前沒有資料", color=discord.Color.red())
            embed.set_footer(text=f"資料更新時間：{str(datetime.datetime.now(timezone)).split('.')[0]}")
            await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))