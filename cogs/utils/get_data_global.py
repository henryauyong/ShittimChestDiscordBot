import requests
import json
from pathlib import Path

pwd = Path(__file__).parent

def update():
    char_data = requests.get("https://api.ennead.cc/buruaka/character")
    char_data = json.loads(char_data.text)

    banner_data = requests.get("https://api.ennead.cc/buruaka/banner")
    banner_data = json.loads(banner_data.text)

    sr = []
    ssr = []
    limited_ssr = []
    fes_ssr = []
    id = []
    old_data = []

    current_banners = []
    # Update old data
    with open((pwd/"../../gacha_data/global/id.json").as_posix(), "r") as f:
        old_data = json.load(f)

    # Get characters image & ID
    with open((pwd/"../../gacha_data/global/id.json").as_posix(), "w") as f:
        old_name = [i["name"] for i in old_data]
        for i in char_data:
            name = i["name"]
            char_id = i["id"]
            if name not in old_name:
                img_data = requests.get(f"https://raw.githubusercontent.com/SchaleDB/SchaleDB/main/images/student/icon/{char_id}.webp").content
                with open((pwd/(f"../../gacha_data/global/image/{name}.png")).as_posix(), "wb") as f2:
                    f2.write(img_data)
                print(f"Added {name}")
            id.append({"name": name , "id": char_id})
        json.dump(id, f, indent=4)
        

    # Get SR characters
    with open((pwd/"../../gacha_data/global/sr.txt").as_posix(), "w") as f:
        for i in char_data:
            if i["baseStar"] == 2 and i["name"] != "Nonomi":
                f.write(i["name"] + "\n")
                sr.append(i["name"])
    

    # Get SSR characters
    for time in banner_data:
        for banner in banner_data[time]:
            if banner["gachaType"] == "LimitedGacha":
                for i in banner["rateups"]:
                    if i not in limited_ssr:
                        limited_ssr.append(i)
            if banner["gachaType"] == "FesGacha":
                for i in banner["rateups"]:
                    if i not in fes_ssr:
                        fes_ssr.append(i)
    with open((pwd/"../../gacha_data/global/ssr.txt").as_posix(), "w") as f:
        for i in char_data:
            if i["baseStar"] == 3 and i["name"] not in limited_ssr and i["name"] not in fes_ssr:
                f.write(i["name"] + "\n")
                ssr.append(i["name"])
    with open((pwd/"../../gacha_data/global/limited_ssr.txt").as_posix(), "w") as f:
        for i in limited_ssr:
            f.write(i + "\n")
    with open((pwd/"../../gacha_data/global/fes_ssr.txt").as_posix(), "w") as f:
        for i in fes_ssr:
            f.write(i + "\n")

    # Get current banner
    for i in banner_data["current"]:
        banner = {}
        banner["gachaType"] = i["gachaType"]
        rateups = []
        for rateup_char in i["rateups"]:
            if rateup_char in sr:
                rateups.append({"name": rateup_char, "raity": "SR"})
            else:
                rateups.append({"name": rateup_char, "raity": "SSR"})
        banner["rateups"] = rateups
        current_banners.append(banner)

    with open((pwd/"../../gacha_data/global/current_banners.json").as_posix(), "w") as f:
        json.dump(current_banners, f, indent=4)
    
    print("Updated global data")

try:
    update()
except Exception as e:
    print(e)
    print("Failed to update global data")
    pass