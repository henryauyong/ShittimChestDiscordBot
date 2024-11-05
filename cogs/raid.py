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
from typing import Optional


pwd = Path(__file__).parent

timezone = pytz.timezone("Asia/Taipei")
# CURRENT_DATETIME = datetime.now(timezone).replace(tzinfo=None)
CURRENT_DATETIME = datetime.strptime("2024-07-02 10:59:00", "%Y-%m-%d %H:%M:%S")

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

message_state = {}

char_id = {}
image_link = {}
translate = {}
with open((pwd / "../raid_data/image.json").as_posix(), "r", encoding="utf-8") as f:
    image_link = json.load(f)
with open((pwd / "../gacha_data/japan/id.json").as_posix(), "r", encoding="utf-8") as f:
    char_id = json.load(f)
with open(
    (pwd / "../raid_data/global/translate.json").as_posix(), "r", encoding="utf-8"
) as f:
    translate = json.load(f)


class RaidLineEmbed(discord.Embed):
    def __init__(self, server: str, current_raid: dict, bot: commands.Bot):
        super().__init__(
            title=f"〖{translate[server]}〗 第{current_raid['season']}期{translate[current_raid['type']]} {translate[current_raid['name']]}",
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

        if current_raid["type"] == "raid":
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
                    if score:
                        if score >= difficulty_scores[difficulty_score]:
                            self.add_field(
                                name=f"{emoji} 第一名：{name}",
                                value=f"分數：{fscore} ({difficulty_score})",
                                inline=False,
                            )
                            break
                    else:
                        self.add_field(
                            name=f"{emoji} 第一名：_無_",
                            value=f"分數：_無_",
                            inline=False,
                        )
                        break
            elif current_raid["type"] == "eliminate_raid":
                # Mapping of display names to actual keys
                groups = raid_db.get_eliminate_raid_groups(
                    server, current_raid["season"]
                )
                categories = {}
                for group in groups:
                    if group == "LightArmor":
                        categories["輕裝甲"] = "light_armor_score"
                    elif group == "HeavyArmor":
                        categories["重裝甲"] = "heavy_armor_score"
                    elif group == "Unarmed":
                        categories["神祕裝甲"] = "unarmed_score"
                    elif group == "ElasticArmor":
                        categories["彈力裝甲"] = "elastic_armor_score"

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


class RaidUserEmbed(discord.Embed):
    def __init__(
        self, server: str, user_data: dict, current_raid: dict, bot: commands.Bot
    ):
        super().__init__(
            title=f"〖{translate[server]}〗{user_data.get('name')} 在 {translate[current_raid['name']]} 的排名",
            color=discord.Color.blue(),
        )

        emoji = ""
        icon_id = user_data.get("icon_id")
        rank = user_data.get("rank")
        tier = user_data.get("tier")
        score = user_data.get("score")
        type = current_raid["type"]
        update_time = user_data.get("update_time")
        if tier == 4:
            emoji = bot.get_emoji(1257306020607430659)
        elif tier == 3:
            emoji = bot.get_emoji(1257307551213686857)
        elif tier == 2:
            emoji = bot.get_emoji(1257307549804400641)
        elif tier == 1:
            emoji = bot.get_emoji(1257307548424474675)

        self.set_thumbnail(
            url=f"https://raw.githubusercontent.com/SchaleDB/SchaleDB/main/images/student/icon/{icon_id}.webp"
        )
        self.add_field(name="排名", value=f"{emoji} {rank} 名", inline=False)
        self.set_footer(text=f"資料更新時間：{update_time}")
        if type == "raid":
            for difficulty_score in reversed(difficulty_scores):
                if score >= difficulty_scores[difficulty_score]:
                    self.add_field(
                        name="分數",
                        value=f"{score:,} ({difficulty_score})",
                        inline=False,
                    )
                    break
        elif type == "eliminate_raid":
            groups = raid_db.get_eliminate_raid_groups(server, current_raid["season"])
            categories = {}
            for group in groups:
                if group == "LightArmor":
                    categories["輕裝甲"] = "light_armor_score"
                elif group == "HeavyArmor":
                    categories["重裝甲"] = "heavy_armor_score"
                elif group == "Unarmed":
                    categories["神祕裝甲"] = "unarmed_score"
                elif group == "ElasticArmor":
                    categories["彈力裝甲"] = "elastic_armor_score"

            details = "\n".join(
                [
                    f"{display_name}: {self.format_score('', user_data.get(actual_key))[1]}"
                    for display_name, actual_key in categories.items()
                ]
            )

            self.add_field(name="總分", value=f"{score:,}", inline=False)
            self.add_field(name="詳細分數", value=details, inline=False)

    def format_score(self, name, score):
        if score:
            score = int(score)
            return name, f"{score:,}"
        return "_無_", "_無_"
    

class BrokenEmbed(discord.Embed):
    def __init__(self):
        super().__init__(
            title="伺服器壞掉了",
            description="無限期停止服務",
            color=discord.Color.red(),
        )
        self.set_footer(
            text=f"資料更新時間： :st_atsuko_grin:"
        )
        self.set_thumbnail(url="https://i.redd.it/zssakw8wpj4a1.jpg")
        self.set_image(url="https://cdn.discordapp.com/attachments/1155803449699618887/1303021502228074546/image0.jpg?ex=672ae597&is=67299417&hm=455a78c3b51d8affaf3327c649961968bfbb3ac19b9c9bae7868c50479ccaad9&")


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="raid-line", description="查看當期總力戰/大決戰檔線")
    @app_commands.describe(server="選擇伺服器")
    @app_commands.choices(
        server=[
            app_commands.Choice(name="國際服", value="global"),
            app_commands.Choice(name="日服", value="japan"),
        ]
    )
    async def raid(
        self, interaction: discord.Interaction, server: app_commands.Choice[str]
    ):
        embed = BrokenEmbed()
        await interaction.response.send_message(embed=embed)
        return


        server = server.value
        status = raid_db.check_current_raid(server)
        if status == "True":
            current_raid = raid_db.get_current_raid(server)
            embed = RaidLineEmbed(
                server,
                current_raid,
                self.bot,
            )
            await interaction.response.send_message(embed=embed)
        elif status == "Ready":
            current_raid = raid_db.get_current_raid(server)
            embed = ReadyEmbed(
                server,
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
    @app_commands.describe(server="選擇伺服器", user="暱稱", tier="檔次", score="總分大於")
    @app_commands.choices(
        server=[
            app_commands.Choice(name="國際服", value="global"),
            app_commands.Choice(name="日服", value="japan"),
        ],
        tier=[
            app_commands.Choice(name="銀", value=2),
            app_commands.Choice(name="金", value=3),
            app_commands.Choice(name="白金", value=4),
        ],
    )
    async def raid_user_search(
        self,
        interaction: discord.Interaction,
        server: app_commands.Choice[str],
        user: str,
        tier: Optional[app_commands.Choice[int]] = None,
        score: Optional[int] = None,
    ):
        embed = BrokenEmbed()
        await interaction.response.send_message(embed=embed)
        return


        server = server.value
        status = raid_db.check_current_raid(server)
        if status == "True":
            current_raid = raid_db.get_current_raid(server)
            type = current_raid["type"]
            raid_user_embeds = []
            tier = tier.value if tier else None
            results = raid_db.get_all_users_rank_by_name(server, type, user, tier, score)
            result_count = len(results)
            for result in results:
                raid_user_embeds.append(
                    RaidUserEmbed(server, result, current_raid, self.bot)
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
                embed.set_footer(
                    text=f"資料更新時間：{datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await interaction.response.send_message(embed=embed)
        elif status == "Ready":
            current_raid = raid_db.get_current_raid(server)
            embed = ReadyEmbed(
                server,
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
