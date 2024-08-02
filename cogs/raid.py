from discord.ext import commands
import discord
import json
from discord import app_commands
from pathlib import Path
import datetime
import pytz
from datetime import timedelta
from datetime import datetime
import sqlite3
from cogs.utils import raid_db


pwd = Path(__file__).parent

timezone = pytz.timezone("Asia/Taipei")
# CURRENT_DATETIME = datetime.now(timezone).replace(tzinfo=None)
CURRENT_DATETIME = datetime.strptime("2024-07-02 10:59:00", "%Y-%m-%d %H:%M:%S")

message_state = {}

char_id = {}
image_link = {}
with open((pwd / "../raid_data/image.json").as_posix(), "r", encoding="utf-8") as f:
    image_link = json.load(f)
with open((pwd / "../gacha_data/japan/id.json").as_posix(), "r", encoding="utf-8") as f:
    char_id = json.load(f)

translate = {}

with open(
    (pwd / "../raid_data/global/translate.json").as_posix(), "r", encoding="utf-8"
) as f:
    translate = json.load(f)


class RaidLineEmbed(discord.Embed):
    def __init__(self, server: str, current_raid: dict, bot: commands.Bot):
        super().__init__(
            title=f"{translate[server]} 第{current_raid['season']}期{translate[current_raid['type']]} {translate[current_raid['name']]}",
            description=f"{str(current_raid['start_date'])} - {str(current_raid['end_date'])}",
            color=discord.Color.blue(),
        )
        self.set_thumbnail(url=image_link[current_raid["name"]])
        self.set_footer(text=f"資料更新時間：{current_raid['update_time']}")

        emojis = {
            "plat": bot.get_emoji(1257306020607430659),
            "gold": bot.get_emoji(1257307551213686857),
            "silver": bot.get_emoji(1257307549804400641),
        }

        score_data = raid_db.get_highest_rank_user_each_tier(
            server, current_raid["type"]
        )

        # normal, hard, veryhard, hardcore, extreme, insane, torment
        difficulty_scores = {
            "normal": 0,
            "hard": 1000000,
            "veryhard": 2000000,
            "hardcore": 4000000,
            "extreme": 8000000,
            "insane": 16000000,
            "torment": 30000000,
        }

        difficulty_count = raid_db.get_difficulty_count(
            server, current_raid["type"], difficulty_scores
        )
        self.description += f"\n\nTORMENT 通關人數：{difficulty_count[1]} 人\nINSANE 通關人數：{difficulty_count[0]} 人"

        for tier, emoji in emojis.items():
            tier_data = score_data[tier]
            name, fscore = self.format_score(
                tier_data.get("name"), tier_data.get("score")
            )
            score = tier_data.get("score")
            if current_raid["type"] == "raid":
                for difficulty_score in reversed(difficulty_scores):
                    if score >= difficulty_scores[difficulty_score]:
                        self.add_field(
                            name=f"{emoji} 第一名：{name}",
                            value=f"分數：{fscore} ({difficulty_score})",
                            inline=False,
                        )
                        break
            elif current_raid["type"] == "eliminate_raid":
                # Mapping of display names to actual keys
                categories = {
                    "輕裝甲": "light_armor_score",
                    "重裝甲": "heavy_armor_score",
                    "神祕裝甲": "unarmed_score",
                }
                details = "\n".join(
                    [
                        f"{display_name}: {self.format_score('', tier_data.get(actual_key))[1]}"
                        for display_name, actual_key in categories.items()
                    ]
                )
                self.add_field(
                    name=f"{emoji} 第一名：{name}",
                    value=f"總分：{fscore}\n{details}",
                    inline=False,
                )

    def format_score(self, name, score):
        if score:
            score = int(score)
            return name, f"{score:,}"
        return "_無_", "_無_"


class ReadyEmbed(discord.Embed):
    def __init__(
        self,
        server: str,
        current_raid: dict,
    ):
        type = current_raid["type"]
        season = current_raid["season"]
        name = current_raid["name"]
        start_date = current_raid["start_date"]
        end_date = current_raid["end_date"]
        super().__init__(
            title=f"{translate[server]} 第{season}期{translate[type]} {translate[name]}",
            description=f"{str(start_date)} - {str(end_date)}",
            color=discord.Color.blue(),
        )
        self.set_thumbnail(url=image_link[name])
        self.add_field(name="正在準備資料", value="", inline=False)
        self.set_footer(
            text=f"資料更新時間：{str(datetime.now(timezone).replace(tzinfo=None)).split('.')[0]}"
        )


class RaidUserView(discord.ui.View):
    def __init__(self, current_page: int, result_count: int, bot: commands.Bot):
        super().__init__(timeout=60)
        self.message = None
        self.add_item(self.FirstPageButton(current_page))
        self.add_item(self.PreviousPageButton(current_page))
        self.add_item(self.PageNumberButton(current_page, result_count))
        self.add_item(self.NextPageButton(current_page, result_count))
        self.add_item(self.LastPageButton(current_page, result_count))

    async def on_timeout(self):
        try:
            message_state.pop(self.message.id)
            await self.message.edit(view=None)
        except discord.NotFound:
            pass
        except AttributeError:
            pass

    class FirstPageButton(discord.ui.Button):
        def __init__(self, current_page: int):
            if current_page == 1:
                super().__init__(
                    style=discord.ButtonStyle.primary, label="⏮️", row=1, disabled=True
                )
            else:
                super().__init__(style=discord.ButtonStyle.primary, label="⏮️", row=1)

        async def callback(self, interaction: discord.Interaction):
            messgae = interaction.message
            message_id = messgae.id
            current_page = message_state[message_id]["current_page"]
            total_page = message_state[message_id]["total_page"]
            embeds = message_state[message_id]["embeds"]
            if current_page > 1:
                current_page = 1
                new_view = RaidUserView(current_page, total_page, interaction.user.bot)
                await interaction.response.edit_message(
                    embed=embeds[current_page - 1], view=new_view
                )
                message_state[message_id]["current_page"] = current_page

    class PreviousPageButton(discord.ui.Button):
        def __init__(self, current_page: int):
            if current_page == 1:
                super().__init__(
                    style=discord.ButtonStyle.primary, label="◀️", row=1, disabled=True
                )
            else:
                super().__init__(style=discord.ButtonStyle.primary, label="◀️", row=1)

        async def callback(self, interaction: discord.Interaction):
            messgae = interaction.message
            message_id = messgae.id
            current_page = message_state[message_id]["current_page"]
            total_page = message_state[message_id]["total_page"]
            embeds = message_state[message_id]["embeds"]
            if current_page > 1:
                current_page -= 1
                new_view = RaidUserView(current_page, total_page, interaction.user.bot)
                await interaction.response.edit_message(
                    embed=embeds[current_page - 1], view=new_view
                )
                message_state[message_id]["current_page"] = current_page

    class PageNumberButton(discord.ui.Button):
        def __init__(self, current_page: int, total_page: int):
            super().__init__(
                style=discord.ButtonStyle.secondary,
                label=f"搜尋結果：{current_page}/{total_page}",
                row=1,
                disabled=True,
            )

        async def callback(self):
            pass

    class NextPageButton(discord.ui.Button):
        def __init__(self, current_page: int, total_page: int):
            if current_page == total_page:
                super().__init__(
                    style=discord.ButtonStyle.primary, label="▶️", row=1, disabled=True
                )
            else:
                super().__init__(style=discord.ButtonStyle.primary, label="▶️", row=1)

        async def callback(self, interaction: discord.Interaction):
            messgae = interaction.message
            message_id = messgae.id
            current_page = message_state[message_id]["current_page"]
            total_page = message_state[message_id]["total_page"]
            embeds = message_state[message_id]["embeds"]
            if current_page < total_page:
                current_page += 1
                new_view = RaidUserView(current_page, total_page, interaction.user.bot)
                await interaction.response.edit_message(
                    embed=embeds[current_page - 1], view=new_view
                )
                message_state[message_id]["current_page"] = current_page

    class LastPageButton(discord.ui.Button):
        def __init__(self, current_page: int, total_page: int):
            if current_page == total_page:
                super().__init__(
                    style=discord.ButtonStyle.primary, label="⏭️", row=1, disabled=True
                )
            else:
                super().__init__(style=discord.ButtonStyle.primary, label="⏭️", row=1)

        async def callback(self, interaction: discord.Interaction):
            messgae = interaction.message
            message_id = messgae.id
            current_page = message_state[message_id]["current_page"]
            total_page = message_state[message_id]["total_page"]
            embeds = message_state[message_id]["embeds"]
            if current_page < total_page:
                current_page = total_page
                new_view = RaidUserView(current_page, total_page, interaction.user.bot)
                await interaction.response.edit_message(
                    embed=embeds[current_page - 1], view=new_view
                )
                message_state[message_id]["current_page"] = current_page


def raid_user_embed(
    type: str, user_data: dict, raid_name: str, update_time: str, bot: commands.Bot
):
    emoji = ""
    name = user_data.get("name")
    icon_id = user_data.get("icon_id")
    rank = user_data.get("rank")
    tier = user_data.get("tier")
    score = user_data.get("score")
    if tier == 4:
        emoji = bot.get_emoji(1257306020607430659)
    elif tier == 3:
        emoji = bot.get_emoji(1257307551213686857)
    elif tier == 2:
        emoji = bot.get_emoji(1257307549804400641)
    elif tier == 1:
        emoji = bot.get_emoji(1257307548424474675)

    if type == "eliminate_raid":
        unarmed_score = user_data.get("unarmed_score")
        heavy_armor_score = user_data.get("heavy_armor_score")
        light_armor_score = user_data.get("light_armor_score")
    embed = discord.Embed(
        title=f"{name} 在 {translate[raid_name]} 的排名",
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(
        url=f"https://raw.githubusercontent.com/SchaleDB/SchaleDB/main/images/student/icon/{icon_id}.webp"
    )
    if type == "raid":
        embed.add_field(name="分數", value=f"{score:,}", inline=False)
    elif type == "eliminate_raid":
        embed.add_field(name="總分", value=f"{score:,}", inline=False)
        embed.add_field(name="輕裝甲", value=f"{light_armor_score:,}", inline=False)
        embed.add_field(name="重裝甲", value=f"{heavy_armor_score:,}", inline=False)
        embed.add_field(name="神祕裝甲", value=f"{unarmed_score:,}", inline=False)

    embed.add_field(name="排名", value=f"{emoji} {rank}", inline=False)
    embed.set_footer(text=f"資料更新時間：{update_time}")
    return embed


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="raid-line", description="查看當期總力戰/大決戰檔線")
    async def raid(self, interaction: discord.Interaction):
        status = raid_db.check_current_raid("global")
        if status == "True":
            current_raid = raid_db.get_current_raid("global")
            embed = RaidLineEmbed(
                "global",
                current_raid,
                self.bot,
            )
            await interaction.response.send_message(embed=embed)
        elif status == "Ready":
            current_raid = raid_db.get_current_raid("global")
            embed = ReadyEmbed(
                "global",
                current_raid,
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="奇普托斯目前爲和平狀態", color=discord.Color.red()
            )
            embed.set_footer(
                text=f"資料更新時間：{str(datetime.now(timezone).replace(tzinfo=None)).split('.')[0]}"
            )
            embed.set_thumbnail(url=image_link["Arona_peace"])
            await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="raid-user-search", description="查看指定玩家在當期總力戰/大決戰的排名"
    )
    async def raid_user_search(self, interaction: discord.Interaction, user: str):
        status = raid_db.check_current_raid("global")
        if status == "True":
            current_raid = raid_db.get_current_raid("global")
            name = current_raid["name"]
            type = current_raid["type"]
            update_time = current_raid["update_time"]
            raid_user_embeds = []
            results = raid_db.get_all_users_rank_by_name("global", type, user)
            result_count = len(results)
            for result in results:
                raid_user_embeds.append(
                    raid_user_embed(type, result, name, update_time, self.bot)
                )

            if result_count == 1:
                await interaction.response.send_message(embed=raid_user_embeds[0])
            if result_count > 1:
                view = RaidUserView(1, result_count, self.bot)
                await interaction.response.send_message(
                    embed=raid_user_embeds[0], view=view
                )
                messgae = await interaction.original_response()
                message_state[messgae.id] = {
                    "current_page": 1,
                    "total_page": result_count,
                    "embeds": raid_user_embeds,
                }
                view.message = messgae
            if result_count == 0:
                embed = discord.Embed(
                    title=f"沒有 {user} 的資料", color=discord.Color.red()
                )
                embed.set_footer(text=f"資料更新時間：{update_time}")
                await interaction.response.send_message(embed=embed)
        elif status == "Ready":
            current_raid = raid_db.get_current_raid("global")
            embed = ReadyEmbed(
                "global",
                current_raid,
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="奇普托斯目前爲和平狀態",
                description="_現在都沒有總力戰還在稽查別人阿_",
                color=discord.Color.red(),
            )
            embed.set_footer(
                text=f"資料更新時間：{str(datetime.now(timezone).replace(tzinfo=None)).split('.')[0]}"
            )
            embed.set_thumbnail(url=image_link["Arona_peace"])
            await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))
