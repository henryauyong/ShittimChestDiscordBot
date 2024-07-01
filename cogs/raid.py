from discord.ext import commands
import discord
import json
from discord import app_commands
from pathlib import Path
import datetime
import pytz

pwd = Path(__file__).parent

timezone = pytz.timezone('Asia/Taipei')

image_link = {}
with open((pwd/"../raid_data/image.json").as_posix(), "r", encoding="utf-8") as f:
    image_link = json.load(f)

translate = {}
global_current_raid = {}
global_current_raid_users = []
with open((pwd/"../raid_data/global/current_raid.json").as_posix(), "r", encoding="utf-8") as f:
    global_current_raid = json.load(f)
with open((pwd/"../raid_data/global/translate.json").as_posix(), "r", encoding="utf-8") as f:
    translate = json.load(f)
with open((pwd/"../raid_data/global/current_raid_users.json").as_posix(), "r", encoding="utf-8") as f:
    global_current_raid_users = json.load(f)
if global_current_raid:
    global_type = global_current_raid["Type"]
    global_season = global_current_raid["Season"]
    global_name = global_current_raid["Name"]
    global_update_time = global_current_raid["UpdateTime"]
    global_start_data = global_current_raid["StartData"]
    global_end_data = global_current_raid["EndData"]

class RaidLineEmbed(discord.Embed):
    def __init__(self, server: str, bot: commands.Bot):
        plat_emoji = bot.get_emoji(1257306020607430659)
        gold_emoji = bot.get_emoji(1257307551213686857)
        silver_emoji = bot.get_emoji(1257307549804400641)
        bronze_emoji = bot.get_emoji(1257307548424474675)

        if server == "國際服":
            type = global_type
            season = global_season
            name = global_name
            update_time = global_update_time
            current_raid = global_current_raid
            plat_score = current_raid["Platinum"]["Score"]
            plat_name = current_raid["Platinum"]["Name"]
            if plat_score:
                plat_score = f'{plat_score:,}'
            else:
                plat_name = "_無_"
                plat_score = "_無_"
            gold_score = current_raid["Gold"]["Score"]
            gold_name = current_raid["Gold"]["Name"]
            if gold_score:
                gold_score = f'{gold_score:,}'
            else:
                gold_name = "_無_"
                gold_score = "_無_"
            silver_score = current_raid["Silver"]["Score"]
            silver_name = current_raid["Silver"]["Name"]
            if silver_score:
                silver_score = f'{silver_score:,}'
            else:
                silver_name = "_無_"
                silver_score = "_無_"

        super().__init__(title=f'{server} 第{season}期{type} {translate[name]}',description=f'{global_start_data} - {global_end_data}', color=discord.Color.blue())
        self.set_thumbnail(url=image_link[name])
        self.add_field(name=f'{plat_emoji} 第一名：{plat_name}', value=f'分數：{plat_score}', inline=False)
        self.add_field(name=f'{gold_emoji} 第一名：{gold_name}', value=f'分數：{gold_score}', inline=False)
        self.add_field(name=f'{silver_emoji} 第一名：{silver_name}', value=f'分數：{silver_score}', inline=False)
        self.set_footer(text=f'資料更新時間：{update_time}')

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='raid-line', description='查看當期總力戰/大決戰檔線')
    async def raid(self, interaction: discord.Interaction):
        if global_current_raid:
            embed = RaidLineEmbed("國際服", self.bot)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="奇普托斯目前爲和平狀態", color=discord.Color.red())
            embed.set_footer(text=f"資料更新時間：{str(datetime.datetime.now(timezone)).split('.')[0]}")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='raid-user-search', description='查看指定玩家在當期總力戰/大決戰的排名')
    async def raid_user_search(self, interaction: discord.Interaction, user: str):
        if global_current_raid:
            found = False
            for i in global_current_raid_users:
                if i["Name"] == user:
                    user_data = i
                    emoji = ''
                    if user_data["Tier"] == 4:
                        emoji = self.bot.get_emoji(1257306020607430659)
                    elif user_data["Tier"] == 3:
                        emoji = self.bot.get_emoji(1257307551213686857)
                    elif user_data["Tier"] == 2:
                        emoji = self.bot.get_emoji(1257307549804400641)
                    elif user_data["Tier"] == 1:
                        emoji = self.bot.get_emoji(1257307548424474675)
                    embed = discord.Embed(title=f'{user} 在 {translate[global_name]} 的排名', color=discord.Color.blue())
                    embed.add_field(name="總分", value=f'{user_data["Score"]:,}', inline=False)
                    embed.add_field(name="排名", value=f'{emoji} {user_data["Rank"]}', inline=False)
                    embed.set_footer(text=f'資料更新時間：{global_update_time}')
                    await interaction.response.send_message(embed=embed)
                    found = True
                    break
            if not found:
                await interaction.response.send_message(f"找不到 {user} 的資料")
        else:
            embed = discord.Embed(title="奇普托斯目前爲和平狀態", description="_現在都沒有總力戰還在稽查別人阿_", color=discord.Color.red())
            embed.set_footer(text=f"資料更新時間：{str(datetime.datetime.now(timezone)).split('.')[0]}")
            await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))