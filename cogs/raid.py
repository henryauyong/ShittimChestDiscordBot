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

pwd = Path(__file__).parent

timezone = pytz.timezone("Asia/Taipei")
CURRENT_DATETIME = datetime.now(timezone).replace(tzinfo=None)
# CURRENT_DATETIME = datetime.strptime("2024-07-02 09:59:00", "%Y-%m-%d %H:%M:%S")

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
    def __init__(self, server: str, type: str, season: int, name: str, start_date: datetime, end_date: datetime, update_time:str, bot: commands.Bot):
        plat_emoji = bot.get_emoji(1257306020607430659)
        gold_emoji = bot.get_emoji(1257307551213686857)
        silver_emoji = bot.get_emoji(1257307549804400641)
        bronze_emoji = bot.get_emoji(1257307548424474675)

        con = sqlite3.connect((pwd / f"../raid_data/{server}_raid.db").as_posix())
        cur = con.cursor()
        score_data = []
        for i in range(1, 5):
            result = cur.execute(
            f"""
            SELECT r1.name, r1.score
            FROM {type}_opponent_list r1
            JOIN (
                SELECT MIN(rank) as min_rank
                FROM raid_opponent_list
                WHERE tier = ?
            ) r2
            ON r1.rank = r2.min_rank
            WHERE r1.tier = ?;
            """,
            [i, i]
            )
            score_data.append(result.fetchall())
        plat_score = list(score_data[3][0])[1]
        plat_name = list(score_data[3][0])[0]
        if plat_score:
            plat_score = f"{plat_score:,}"
        else:
            plat_name = "_無_"
            plat_score = "_無_"
        gold_score = list(score_data[2][0])[1]
        gold_name = list(score_data[2][0])[0]
        if gold_score:
            gold_score = f"{gold_score:,}"
        else:
            gold_name = "_無_"
            gold_score = "_無_"
        silver_score = list(score_data[1][0])[1]
        silver_name = list(score_data[1][0])[0]
        if silver_score:
            silver_score = f"{silver_score:,}"
        else:
            silver_name = "_無_"
            silver_score = "_無_"

        super().__init__(
            title=f"{translate[server]} 第{season}期{translate[type]} {translate[name]}",
            description=f"{str(start_date)} - {str(end_date)}",
            color=discord.Color.blue(),
        )
        self.set_thumbnail(url=image_link[name])
        self.add_field(
            name=f"{plat_emoji} 第一名：{plat_name}",
            value=f"分數：{plat_score}",
            inline=False,
        )
        self.add_field(
            name=f"{gold_emoji} 第一名：{gold_name}",
            value=f"分數：{gold_score}",
            inline=False,
        )
        self.add_field(
            name=f"{silver_emoji} 第一名：{silver_name}",
            value=f"分數：{silver_score}",
            inline=False,
        )
        self.set_footer(text=f"資料更新時間：{update_time}")


class ReadyEmbed(discord.Embed):
    def __init__(self, server: str, type: str, season: int, name: str, start_date: datetime, end_date: datetime, bot: commands.Bot):
        super().__init__(
            title=f"{translate[server]} 第{season}期{translate[type]} {translate[name]}",
            description=f"{str(start_date)} - {str(end_date)}",
            color=discord.Color.blue(),
        )
        self.set_thumbnail(url=image_link[name])
        self.add_field(name="正在準備資料", value="", inline=False)
        self.set_footer(text=f"資料更新時間：{str(datetime.now(timezone).replace(tzinfo=None)).split('.')[0]}")


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


def raid_user_embed(user_data: list, global_name:str, global_update_time:str, bot: commands.Bot):
    emoji = ""
    name = user_data[0]
    icon_id = user_data[1]
    rank = user_data[2]
    tier = user_data[3]
    score = user_data[4]
    if tier == 4:
        emoji = bot.get_emoji(1257306020607430659)
    elif tier == 3:
        emoji = bot.get_emoji(1257307551213686857)
    elif tier == 2:
        emoji = bot.get_emoji(1257307549804400641)
    elif tier == 1:
        emoji = bot.get_emoji(1257307548424474675)
    embed = discord.Embed(
        title=f"{name} 在 {translate[global_name]} 的排名",
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(
        url=f"https://raw.githubusercontent.com/SchaleDB/SchaleDB/main/images/student/icon/{icon_id}.webp"
    )
    embed.add_field(name="總分", value=f"{score:,}", inline=False)
    embed.add_field(name="排名", value=f"{emoji} {rank}", inline=False)
    embed.set_footer(text=f"資料更新時間：{global_update_time}")
    return embed

def check_current_raid(server: str):
    con = sqlite3.connect((pwd / f"../raid_data/{server}_raid.db").as_posix())
    cur = con.cursor()
    ta_results = cur.execute(
    """
    SELECT start_data, end_data
    FROM raid_season_manage_excel_table
    ORDER BY season_id DESC
    LIMIT 5;
    """
    )
    ta_results = ta_results.fetchall()
    for result in ta_results:
        result = list(result)
        start_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date:
            if current_date - timedelta(hours=2) <= start_date:
                con.close()
                return "Ready"
            con.close()
            return "True"
    ga_results = cur.execute(
    """
    SELECT start_data, end_data
    FROM eliminate_raid_season_manage_excel_table
    ORDER BY season_id DESC
    LIMIT 5;
    """
    )
    ga_results = ga_results.fetchall()
    for result in ga_results:
        result = list(result)
        start_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date:
            if current_date - timedelta(hours=2) <= start_date:
                con.close()
                return "Ready"
            con.close()
            return "True"
    con.close()
    return "False"

def get_current_raid(server:str):
    con = sqlite3.connect((pwd / f"../raid_data/{server}_raid.db").as_posix())
    cur = con.cursor()
    ta_results = cur.execute(
    """
    SELECT season_display, name, start_data, end_data
    FROM raid_season_manage_excel_table
    ORDER BY season_id DESC
    LIMIT 5;
    """
    )
    ta_results = ta_results.fetchall()
    update_time = cur.execute(
    """
    SELECT update_time
    FROM raid_update_time
    """
    )
    update_time = list(update_time.fetchall()[0])[0]
    for result in ta_results:
        result = list(result)
        start_date = datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date:
            season_display = result[0]
            name = result[1]
            con.close()
            return "raid", season_display, name, start_date, end_date, update_time
    ga_results = cur.execute(
    """
    SELECT season_display, name, start_data, end_data
    FROM eliminate_raid_season_manage_excel_table
    ORDER BY season_id DESC
    LIMIT 5;
    """
    )
    ga_results = ga_results.fetchall()
    for result in ga_results:
        result = list(result)
        start_date = datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date:
            season_display = result[0]
            name = result[1]
            con.close()
            return "eliminate_raid", season_display, name, start_date, end_date, update_time
    con.close()
    return None

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="raid-line", description="查看當期總力戰/大決戰檔線")
    async def raid(self, interaction: discord.Interaction):
        if check_current_raid("global") == "True":
            type, season_display, name, start_date, end_date, update_time = get_current_raid("global")
            embed = RaidLineEmbed("global", type, season_display, name, start_date, end_date, update_time, self.bot)
            await interaction.response.send_message(embed=embed)
        elif check_current_raid("global") == "Ready":
            type, season_display, name, start_date, end_date = get_current_raid("global")
            embed = ReadyEmbed
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
        if check_current_raid("global") == "True":
            type, season_display, name, start_date, end_date, update_time = get_current_raid("global")
            raid_user_embeds = []
            con = sqlite3.connect((pwd / "../raid_data/global_raid.db").as_posix())
            cur = con.cursor()

            results = cur.execute(
                "SELECT name, icon_id, rank, tier, score FROM raid_opponent_list WHERE name = ?",
                (user,),
            ).fetchall()
            result_count = len(results)
            for result in results:
                raid_user_embeds.append(raid_user_embed(list(result), name, update_time, self.bot))

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
        else:
            embed = discord.Embed(
                title="奇普托斯目前爲和平狀態",
                description="_現在都沒有總力戰還在稽查別人阿_",
                color=discord.Color.red(),
            )
            embed.set_footer(
                text=f"資料更新時間：{str(CURRENT_DATETIME).split('.')[0]}"
            )
            embed.set_thumbnail(url=image_link["Arona_peace"])
            await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))
