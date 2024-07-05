from pathlib import Path
import json
from datetime import datetime
from datetime import timedelta
import pytz

timezone = pytz.timezone("Asia/Taipei")
CURRENT_DATETIME = datetime.now(timezone).replace(tzinfo=None)
# CURRENT_DATETIME = datetime.strptime("2024-07-02 09:59:00", "%Y-%m-%d %H:%M:%S")

pwd = Path(__file__).parent


def update():
    translated_name = {}
    ta_data = {}
    ga_data = {}
    ta_user_data = {}
    ga_user_data = {}
    current_raid = {}
    current_raid_users = []

    with open(
        (pwd / "../../raid_data/global/translate.json").as_posix(),
        "r",
        encoding="utf-8",
    ) as f:
        translated_name = json.load(f)

    with open(
        (pwd / "../../raid_data/global/RaidSeasonManageExcelTable.json").as_posix(),
        "r",
        encoding="utf-8",
    ) as f:
        with open(
            (
                pwd / "../../raid_data/global/EliminateRaidSeasonManageExcelTable.json"
            ).as_posix(),
            "r",
            encoding="utf-8",
        ) as f2:
            ta_data = json.load(f)["Data"]
            ga_data = json.load(f2)["Data"]
            for i in reversed(ta_data):
                start_date = datetime.strptime(
                    i["SeasonStartData"], "%Y-%m-%d %H:%M:%S"
                ) - timedelta(hours=1)
                end_date = datetime.strptime(
                    i["SeasonEndData"], "%Y-%m-%d %H:%M:%S"
                ) - timedelta(hours=1)
                if start_date < CURRENT_DATETIME and end_date > CURRENT_DATETIME:
                    current_raid["Type"] = "總力戰"
                    current_raid["Season"] = i["SeasonDisplay"]
                    current_raid["Name"] = i["OpenRaidBossGroup"][0].split("_")[0]
                    current_raid["StartData"] = (
                        datetime.strptime(i["SeasonStartData"], "%Y-%m-%d %H:%M:%S")
                        - timedelta(hours=1)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    current_raid["EndData"] = (
                        datetime.strptime(i["SeasonEndData"], "%Y-%m-%d %H:%M:%S")
                        - timedelta(hours=1)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    break
            for i in reversed(ga_data):
                start_date = datetime.strptime(
                    i["SeasonStartData"], "%Y-%m-%d %H:%M:%S"
                ) - timedelta(hours=1)
                end_date = datetime.strptime(
                    i["SeasonEndData"], "%Y-%m-%d %H:%M:%S"
                ) - timedelta(hours=1)
                if start_date < CURRENT_DATETIME and end_date > CURRENT_DATETIME:
                    current_raid["Type"] = "大決戰"
                    current_raid["Season"] = i["SeasonDisplay"]
                    current_raid["Name"] = i["OpenRaidBossGroup01"].split("_")[0]
                    current_raid["StartData"] = i["SeasonStartData"]
                    current_raid["EndData"] = i["SeasonEndData"]
                    break

    if current_raid != {}:
        if current_raid["Type"] == "總力戰":
            with open(
                (pwd / "../../raid_data/global/RaidOpponentList.json").as_posix(),
                "r",
                encoding="utf-8",
            ) as f:
                ta_data = json.load(f)
                ta_user_data = ta_data["OpponentUserDBs"]

                with open(
                    (pwd / "../../raid_data/global/current_raid_users.json").as_posix(),
                    "w",
                    encoding="utf-8",
                ) as f2:
                    for i in ta_user_data:
                        current_raid_user = {}
                        current_raid_user["AccountId"] = i["AccountId"]
                        current_raid_user["Name"] = i["Nickname"]
                        current_raid_user["IconId"] = i["RepresentCharacterUniqueId"]
                        current_raid_user["Rank"] = i["Rank"]
                        current_raid_user["Tier"] = i["Tier"]
                        current_raid_user["Score"] = i["BestRankingPoint"]
                        current_raid_users.append(current_raid_user)
                    data_tuples = [(d["AccountId"], d) for d in current_raid_users]
                    data_tuples = list(dict(data_tuples).values())
                    current_raid_users = [dict(t) for t in data_tuples]
                    json.dump(current_raid_users, f2, indent=4, ensure_ascii=False)

                plat_user = [i for i in ta_user_data if i["Tier"] == 4]
                if plat_user:
                    Platinum = {}
                    Platinum["Name"] = plat_user[0]["Nickname"]
                    Platinum["Score"] = plat_user[0]["BestRankingPoint"]
                    current_raid["Platinum"] = Platinum
                else:
                    Platinum = {}
                    Platinum["Name"] = None
                    Platinum["Score"] = None
                    current_raid["Platinum"] = Platinum
                gold_user = [i for i in ta_user_data if i["Tier"] == 3]
                if gold_user:
                    Gold = {}
                    Gold["Name"] = gold_user[0]["Nickname"]
                    Gold["Score"] = gold_user[0]["BestRankingPoint"]
                    current_raid["Gold"] = Gold
                else:
                    Gold = {}
                    Gold["Name"] = None
                    Gold["Score"] = None
                    current_raid["Gold"] = Gold
                silver_user = [i for i in ta_user_data if i["Tier"] == 2]
                if silver_user:
                    Silver = {}
                    Silver["Name"] = silver_user[0]["Nickname"]
                    Silver["Score"] = silver_user[0]["BestRankingPoint"]
                    current_raid["Silver"] = Silver
                else:
                    Silver = {}
                    Silver["Name"] = None
                    Silver["Score"] = None
                    current_raid["Silver"] = Silver
                bronze_user = [i for i in ta_user_data if i["Tier"] == 1]
                if bronze_user:
                    Bronze = {}
                    Bronze["Name"] = bronze_user[0]["Nickname"]
                    Bronze["Score"] = bronze_user[0]["BestRankingPoint"]
                    current_raid["Bronze"] = Bronze
                else:
                    Bronze = {}
                    Bronze["Name"] = None
                    Bronze["Score"] = None
                    current_raid["Bronze"] = Bronze
                temp_time = ta_data["timestamp"].split(".")[0].replace("T", " ")
                temp_time = datetime.strptime(
                    temp_time, "%Y-%m-%d %H:%M:%S"
                ) + timedelta(hours=8)
                current_raid["UpdateTime"] = temp_time.strftime("%Y-%m-%d %H:%M:%S")

        elif current_raid["Type"] == "大決戰":
            with open(
                (
                    pwd / "../../raid_data/global/EliminateRaidOpponentList.json"
                ).as_posix(),
                "r",
                encoding="utf-8",
            ) as f2:
                ga_data = json.load(f2)
                ga_user_data = ga_data["OpponentUserDBs"]

                with open(
                    (pwd / "../../raid_data/global/current_raid_users.json").as_posix(),
                    "w",
                    encoding="utf-8",
                ) as f2:
                    for i in ga_user_data:
                        current_raid_user = {}
                        current_raid_user["AccountId"] = i["AccountId"]
                        current_raid_user["Name"] = i["Nickname"]
                        current_raid_user["IconId"] = i["RepresentCharacterUniqueId"]
                        current_raid_user["Rank"] = i["Rank"]
                        current_raid_user["Tier"] = i["Tier"]
                        current_raid_user["Score"] = i["BestRankingPoint"]
                        current_raid_user["UnarmedScore"] = [
                            value
                            for key, value in i["BossGroupToRankingPoint"].items()
                            if "Unarmed" in key
                        ][0]
                        current_raid_user["HeavyArmorScore"] = [
                            value
                            for key, value in i["BossGroupToRankingPoint"].items()
                            if "HeavyArmor" in key
                        ][0]
                        current_raid_user["LightArmorScore"] = [
                            value
                            for key, value in i["BossGroupToRankingPoint"].items()
                            if "LightArmor" in key
                        ][0]
                        current_raid_users.append(current_raid_user)
                    data_tuples = [(d["AccountId"], d) for d in current_raid_users]
                    data_tuples = list(dict(data_tuples).values())
                    current_raid_users = [dict(t) for t in data_tuples]
                    json.dump(current_raid_users, f2, indent=4, ensure_ascii=False)

                plat_user = [i for i in ga_user_data if i["Tier"] == 4]
                if plat_user:
                    Platinum = {}
                    Platinum["Name"] = plat_user[0]["Nickname"]
                    Platinum["Score"] = plat_user[0]["BestRankingPoint"]
                    Platinum["UnarmedScore"] = [
                        value
                        for key, value in plat_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "Unarmed" in key
                    ][0]
                    Platinum["HeavyArmorScore"] = [
                        value
                        for key, value in plat_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "HeavyArmor" in key
                    ][0]
                    Platinum["LightArmorScore"] = [
                        value
                        for key, value in plat_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "LightArmor" in key
                    ][0]
                    current_raid["Platinum"] = Platinum
                else:
                    Platinum = {}
                    Platinum["Name"] = None
                    Platinum["Score"] = None
                    Platinum["UnarmedScore"] = None
                    Platinum["HeavyArmorScore"] = None
                    Platinum["LightArmorScore"] = None
                    current_raid["Platinum"] = Platinum
                gold_user = [i for i in ga_user_data if i["Tier"] == 3]
                if gold_user:
                    Gold = {}
                    Gold["Name"] = gold_user[0]["Nickname"]
                    Gold["Score"] = gold_user[0]["BestRankingPoint"]
                    Gold["UnarmedScore"] = [
                        value
                        for key, value in gold_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "Unarmed" in key
                    ][0]
                    Gold["HeavyArmorScore"] = [
                        value
                        for key, value in gold_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "HeavyArmor" in key
                    ][0]
                    Gold["LightArmorScore"] = [
                        value
                        for key, value in gold_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "LightArmor" in key
                    ][0]
                    current_raid["Gold"] = Gold
                else:
                    Gold = {}
                    Gold["Name"] = None
                    Gold["Score"] = None
                    Gold["UnarmedScore"] = None
                    Gold["HeavyArmorScore"] = None
                    Gold["LightArmorScore"] = None
                    current_raid["Gold"] = Gold
                silver_user = [i for i in ga_user_data if i["Tier"] == 2]
                if silver_user:
                    Silver = {}
                    Silver["Name"] = silver_user[0]["Nickname"]
                    Silver["Score"] = silver_user[0]["BestRankingPoint"]
                    Silver["UnarmedScore"] = [
                        value
                        for key, value in silver_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "Unarmed" in key
                    ][0]
                    Silver["HeavyArmorScore"] = [
                        value
                        for key, value in silver_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "HeavyArmor" in key
                    ][0]
                    Silver["LightArmorScore"] = [
                        value
                        for key, value in silver_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "LightArmor" in key
                    ][0]
                    current_raid["Silver"] = Silver
                else:
                    Silver = {}
                    Silver["Name"] = None
                    Silver["Score"] = None
                    Silver["UnarmedScore"] = None
                    Silver["HeavyArmorScore"] = None
                    Silver["LightArmorScore"] = None
                    current_raid["Silver"] = Silver
                bronze_user = [i for i in ga_user_data if i["Tier"] == 1]
                if bronze_user:
                    Bronze = {}
                    Bronze["Name"] = bronze_user[0]["Nickname"]
                    Bronze["Score"] = bronze_user[0]["BestRankingPoint"]
                    Bronze["UnarmedScore"] = [
                        value
                        for key, value in bronze_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "Unarmed" in key
                    ][0]
                    Bronze["HeavyArmorScore"] = [
                        value
                        for key, value in bronze_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "HeavyArmor" in key
                    ][0]
                    Bronze["LightArmorScore"] = [
                        value
                        for key, value in bronze_user[0][
                            "BossGroupToRankingPoint"
                        ].items()
                        if "LightArmor" in key
                    ][0]
                    current_raid["Bronze"] = Bronze
                else:
                    Bronze = {}
                    Bronze["Name"] = None
                    Bronze["Score"] = None
                    Bronze["UnarmedScore"] = None
                    Bronze["HeavyArmorScore"] = None
                    Bronze["LightArmorScore"] = None
                    current_raid["Bronze"] = Bronze
                temp_time = ta_data["timestamp"].split(".")[0].replace("T", " ")
                temp_time = datetime.strptime(
                    temp_time, "%Y-%m-%d %H:%M:%S"
                ) + timedelta(hours=8)
                current_raid["UpdateTime"] = temp_time.strftime("%Y-%m-%d %H:%M:%S")

    with open(
        (pwd / "../../raid_data/global/current_raid.json").as_posix(),
        "w",
        encoding="utf-8",
    ) as f3:
        json.dump(current_raid, f3, indent=4, ensure_ascii=False)

    print(CURRENT_DATETIME)
