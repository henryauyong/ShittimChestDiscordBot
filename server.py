from flask import Flask, request
import json
from dctoken import *
import pytz
import sqlite3
from datetime import datetime
from datetime import timedelta

TOKEN = server_token
app = Flask(__name__)

timezone = pytz.timezone("Asia/Taipei")


def insert(data: json):
    protocol = data["protocol"]
    if protocol == "Error":
        return
    elif protocol == "Raid_OpponentList":
        con = sqlite3.connect("./raid_data/global_raid.db")
        cur = con.cursor()
        data = json.loads(data["packet"])
        current_raid_users = data["OpponentUserDBs"]
        for user in current_raid_users:
            account_id = user["AccountId"]
            name = user["Nickname"]
            icon_id = user["RepresentCharacterUniqueId"]
            rank = user["Rank"]
            tier = user["Tier"]
            score = user["BestRankingPoint"]
            values = [account_id, name, icon_id, rank, tier, score]
            cur.execute(
                """
                INSERT OR IGNORE INTO raid_opponent_list 
                (account_id, name, icon_id, rank, tier, score) 
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                values,
            )
            cur.execute(
                """
                UPDATE raid_opponent_list 
                SET name = ?, icon_id = ?, rank = ?, tier = ?, score = ? 
                WHERE account_id = ?;
                """,
                values[1:] + values[:1],
            )
        current_time_list = []
        current_time = str(datetime.now(timezone).replace(tzinfo=None)).split(".")[0]
        current_time_list.append(current_time)
        print(current_time_list)
        print(type(current_time_list))
        cur.execute(
            """
            UPDATE raid_update_time
            SET update_time = ?
            """,
            current_time_list,
        )
        con.commit()
        con.close()
    elif protocol == "RaidSeasonManageExcelTable.json":
        con = sqlite3.connect("./raid_data/global_raid.db")
        cur = con.cursor()
        raids = data["Data"]
        for raid in raids:
            season_id = raid["SeasonId"]
            season_display = raid["SeasonDisplay"]
            start_data = (
                datetime.strptime(raid["SeasonStartData"], "%Y-%m-%d %H:%M:%S")
                - timedelta(hours=1)
            ).strftime("%Y-%m-%d %H:%M:%S")
            end_data = (
                datetime.strptime(raid["SeasonEndData"], "%Y-%m-%d %H:%M:%S")
                - timedelta(hours=1)
            ).strftime("%Y-%m-%d %H:%M:%S")
            name = raid["OpenRaidBossGroup"][0].split("_")[0]
            values = [season_id, season_display, name, start_data, end_data]
            cur.execute(
                """
                INSERT OR IGNORE INTO raid_season_manage_excel_table 
                (season_id, season_display, name, start_data, end_data) 
                VALUES (?, ?, ?, ?, ?);
                """,
                values,
            )
            cur.execute(
                """
                UPDATE raid_season_manage_excel_table 
                SET season_display = ?, name = ?, start_data = ?, end_data = ?
                WHERE season_id = ?;
                """,
                values[1:] + values[:1],
            )
        con.commit()
        con.close()
    elif protocol == "EliminateRaid_OpponentList":
        con = sqlite3.connect("./raid_data/global_raid.db")
        cur = con.cursor()
        data = json.loads(data["packet"])
        current_raid_users = data["OpponentUserDBs"]
        for user in current_raid_users:
            account_id = user["AccountId"]
            name = user["Nickname"]
            icon_id = user["RepresentCharacterUniqueId"]
            rank = user["Rank"]
            tier = user["Tier"]
            score = user["BestRankingPoint"]
            unarmed_score = [
                value
                for key, value in user["BossGroupToRankingPoint"].items()
                if "Unarmed" in key
            ][0]
            heavy_armor_score = [
                value
                for key, value in user["BossGroupToRankingPoint"].items()
                if "HeavyArmor" in key
            ][0]
            light_armor_score = [
                value
                for key, value in user["BossGroupToRankingPoint"].items()
                if "LightArmor" in key
            ][0]
            values = [account_id, name, icon_id, rank, tier, score, unarmed_score, heavy_armor_score, light_armor_score]
            cur.execute(
                """
                INSERT OR IGNORE INTO eliminate_raid_opponent_list 
                (account_id, name, icon_id, rank, tier, score, unarmed_score, heavy_armor_score, light_armor_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                values,
            )
            cur.execute(
                """
                UPDATE eliminate_raid_opponent_list 
                SET name = ?, icon_id = ?, rank = ?, tier = ?, score = ?, unarmed_score = ?, heavy_armor_score = ?, light_armor_score = ?
                WHERE account_id = ?;
                """,
                values[1:] + values[:1],
            )
        current_time_list = []
        current_time = str(datetime.now(timezone).replace(tzinfo=None)).split(".")[0]
        current_time_list.append(current_time)
        print(current_time_list)
        print(type(current_time_list))
        cur.execute(
            """
            UPDATE raid_update_time
            SET update_time = ?
            """,
            current_time_list,
        )
        con.commit()
    elif protocol == "EliminateRaidSeasonManageExcelTable.json":
        con = sqlite3.connect("./raid_data/global_raid.db")
        cur = con.cursor()
        raids = data["Data"]
        for raid in raids:
            season_id = raid["SeasonId"]
            season_display = raid["SeasonDisplay"]
            start_data = (
                datetime.strptime(raid["SeasonStartData"], "%Y-%m-%d %H:%M:%S")
                - timedelta(hours=1)
            ).strftime("%Y-%m-%d %H:%M:%S")
            end_data = (
                datetime.strptime(raid["SeasonEndData"], "%Y-%m-%d %H:%M:%S")
                - timedelta(hours=1)
            ).strftime("%Y-%m-%d %H:%M:%S")
            name = raid["OpenRaidBossGroup01"].split("_")[0]
            values = [season_id, season_display, name, start_data, end_data]
            cur.execute(
                """
                INSERT OR IGNORE INTO eliminate_raid_season_manage_excel_table 
                (season_id, season_display, name, start_data, end_data) 
                VALUES (?, ?, ?, ?, ?);
                """,
                values,
            )
            cur.execute(
                """
                UPDATE eliminate_raid_season_manage_excel_table 
                SET season_display = ?, name = ?, start_data = ?, end_data = ?
                WHERE season_id = ?;
                """,
                values[1:] + values[:1],
            )
        con.commit()
        con.close()


@app.route("/", methods=["POST"])
def get_raid_data():
    token = request.headers.get("Token")
    if token != TOKEN:
        return "Invalid Token", 401
    result = ""
    if request.is_json:
        result = "OK"
        data = request.get_json()
        insert(data)
        print(result)
    else:
        result = "Not JSON Data"
        print(result)
    return result


if __name__ == "__main__":
    app.run("0.0.0.0", 9876)
