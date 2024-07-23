from pathlib import Path
from datetime import datetime
from datetime import timedelta
import pytz
import sqlite3

pwd = Path(__file__).parent

timezone = pytz.timezone("Asia/Taipei")
# CURRENT_DATETIME = datetime.now(timezone).replace(tzinfo=None)
CURRENT_DATETIME = datetime.strptime("2024-07-02 12:59:00", "%Y-%m-%d %H:%M:%S")


def get_highest_rank_user_each_tier(server: str, type: str):
    con = sqlite3.connect((pwd / f"../../raid_data/{server}_raid.db").as_posix())
    cur = con.cursor()
    score_data = []
    tier_names = ["silver", "gold", "plat"]
    query = """
            SELECT r1.name, r1.score{extra_fields}
            FROM {table_name} r1
            JOIN (
                SELECT MIN(rank) as min_rank
                FROM {table_name}
                WHERE tier = ?
            ) r2 ON r1.rank = r2.min_rank
            WHERE r1.tier = ?;
            """
    extra_fields = (
        ", r1.unarmed_score, r1.heavy_armor_score, r1.light_armor_score"
        if type != "raid"
        else ""
    )
    table_name = (
        "eliminate_raid_opponent_list" if type != "raid" else "raid_opponent_list"
    )

    for i in range(2, 5):
        result = cur.execute(
            query.format(extra_fields=extra_fields, table_name=table_name), [i, i]
        ).fetchall()
        score_data.append(result)

    return_data = {}
    for idx, tier in enumerate(tier_names):
        if len(score_data[idx]):
            data = list(score_data[idx][0])
            return_data[tier] = {"name": data[0], "score": data[1]}
            if type != "raid":
                return_data[tier].update(
                    {
                        "unarmed_score": data[2],
                        "heavy_armor_score": data[3],
                        "light_armor_score": data[4],
                    }
                )
        else:
            return_data[tier] = {"name": None, "score": None}
            if type != "raid":
                return_data[tier].update(
                    {
                        "unarmed_score": None,
                        "heavy_armor_score": None,
                        "light_armor_score": None,
                    }
                )

    con.close()
    return return_data


def check_current_raid(server: str):
    con = sqlite3.connect((pwd / f"../../raid_data/{server}_raid.db").as_posix())
    cur = con.cursor()
    ta_results = cur.execute(
        """
        SELECT start_data, end_data
        FROM raid_season_manage_excel_table
        ORDER BY season_id DESC
        LIMIT 5;
        """
    ).fetchall()
    for result in ta_results:
        result = list(result)
        start_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date + timedelta(days=7):
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
    ).fetchall()
    for result in ga_results:
        result = list(result)
        start_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date + timedelta(days=7):
            if current_date - timedelta(hours=2) <= start_date:
                con.close()
                return "Ready"
            con.close()
            return "True"
    con.close()
    return "False"


def get_current_raid(server: str):
    con = sqlite3.connect((pwd / f"../../raid_data/{server}_raid.db").as_posix())
    cur = con.cursor()
    ta_results = cur.execute(
        """
        SELECT season_display, name, start_data, end_data
        FROM raid_season_manage_excel_table
        ORDER BY season_id DESC
        LIMIT 5;
        """
    ).fetchall()
    ta_results = ta_results
    update_time = cur.execute(
        """
        SELECT update_time
        FROM raid_update_time
        """
    ).fetchall()
    update_time = list(update_time[0])[0]
    for result in ta_results:
        result = list(result)
        start_date = datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date + timedelta(days=7):
            season_display = result[0]
            name = result[1]
            con.close()
            return_data = {
                "type": "raid",
                "season": season_display,
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "update_time": update_time,
            }
            return return_data
    ga_results = cur.execute(
        """
        SELECT season_display, name, start_data, end_data
        FROM eliminate_raid_season_manage_excel_table
        ORDER BY season_id DESC
        LIMIT 5;
        """
    ).fetchall()
    for result in ga_results:
        result = list(result)
        start_date = datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now(timezone).replace(tzinfo=None)
        if start_date < current_date and current_date < end_date + timedelta(days=7):
            season_display = result[0]
            name = result[1]
            con.close()
            return_data = {
                "type": "eliminate_raid",
                "season": season_display,
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "update_time": update_time,
            }
            return return_data
    con.close()
    return None


def get_all_users_rank_by_name(server: str, type: str, name: str):
    con = sqlite3.connect((pwd / f"../../raid_data/{server}_raid.db").as_posix())
    cur = con.cursor()
    query = """
            SELECT rank, score, icon_id, tier{extra_fields}
            FROM {table_name}
            WHERE name = ?;
            """
    extra_fields = (
        ", unarmed_score, heavy_armor_score, light_armor_score"
        if type != "raid"
        else ""
    )
    table_name = (
        "eliminate_raid_opponent_list" if type != "raid" else "raid_opponent_list"
    )
    result = cur.execute(
        query.format(extra_fields=extra_fields, table_name=table_name), [name]
    ).fetchall()
    return_data = []
    for data in result:
        data = list(data)
        return_data.append(
            {
                "name": name,
                "rank": data[0],
                "score": data[1],
                "icon_id": data[2],
                "tier": data[3],
            }
        )
        if type != "raid":
            return_data[-1].update(
                {
                    "unarmed_score": data[4],
                    "heavy_armor_score": data[5],
                    "light_armor_score": data[6],
                }
            )
    con.close()
    return return_data
