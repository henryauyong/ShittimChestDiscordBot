import requests
import json
from pathlib import Path
import re

pwd = Path(__file__).parent

def update():
    char_data = requests.get("https://schaledb.com/data/jp/students.min.json")
    char_data = json.loads(char_data.text)

    banner_data = requests.get("https://api.ennead.cc/buruaka/banner?region=japan")
    banner_data = json.loads(banner_data.text)

    sr = []
    ssr = []
    limited_ssr = []
    fes_ssr = []
    id = []
    old_data = []

    current_banners = []

    # Translate character name
    with open((pwd/"../../gacha_data/japan/translate.json").as_posix(), "w", encoding="utf-8") as f:
        translate = {}
        for i in char_data:
            name = i["Name"]
            en_name = i["PathName"]
            translate[name] = en_name
        json.dump(translate, f, indent=4, ensure_ascii=False)

    # with open((pwd/"../../gacha_data/japan/raw.json").as_posix(), "w", encoding="utf-8") as f:
    #     json.dump(char_data, f, indent=4, ensure_ascii=False)

    # Update old data
    with open((pwd/"../../gacha_data/japan/id.json").as_posix(), "r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Get character image and ID
    with open((pwd/"../../gacha_data/japan/id.json").as_posix(), "w", encoding="utf-8") as f:
        old_name = [i["name"] for i in old_data]
        for i in char_data:
            name = i["PathName"]
            char_id = i["Id"]
            if name not in old_name:
                img_data = requests.get(f"https://schaledb.com/images/student/icon/{char_id}.webp").content
                with open((pwd/(f"../../gacha_data/japan/image/{name}.png")).as_posix(), "wb") as f2:
                    f2.write(img_data)
                print(f"Added {name}")
            id.append({"name": name , "id": char_id})
        json.dump(id, f, indent=4, ensure_ascii=False)

    # Get R characters
    with open((pwd/"../../gacha_data/japan/r.txt").as_posix(), "w", encoding="utf-8") as f:
        for i in char_data:
            if i["StarGrade"] == 1 and i["IsLimited"] == 0:
                f.write(i["Name"] + "\n")
    
    # Get SR characters
    with open((pwd/"../../gacha_data/japan/sr.txt").as_posix(), "w", encoding="utf-8") as f:
        for i in char_data:
            if i["StarGrade"] == 2 and i["IsLimited"] == 0:
                f.write(i["Name"] + "\n")
                sr.append(i["Name"])
    
    # Get SSR characters
    with open((pwd/"../../gacha_data/japan/ssr.txt").as_posix(), "w", encoding="utf-8") as f:
        for i in char_data:
            if i["StarGrade"] == 3 and i["IsLimited"] == 0:
                f.write(i["Name"] + "\n")
                ssr.append(i["Name"])
    
    # Get Fes SSR characters
    with open((pwd/"../../gacha_data/japan/fes_ssr.txt").as_posix(), "w", encoding="utf-8") as f:
        for time in banner_data:
            for banner in banner_data[time]:
                if banner["gachaType"] == "FesGacha":
                    for i in banner["rateups"]:
                        if i not in fes_ssr:
                            f.write(i + "\n")
                            fes_ssr.append(i)
    
    # Get limited SSR characters
    with open((pwd/"../../gacha_data/japan/limited_ssr.txt").as_posix(), "w", encoding="utf-8") as f:
        for i in char_data:
            if i["StarGrade"] == 3 and i["IsLimited"] == 1:
                limited_ssr.append(i["Name"])
        for i in limited_ssr:
            if i in fes_ssr:
                limited_ssr.remove(i)
        f.write("\n".join(limited_ssr))

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
    
    with open((pwd/"../../gacha_data/japan/current_banners.json").as_posix(), "w", encoding="utf-8") as f:
        json.dump(current_banners, f, indent=4, ensure_ascii=False)

    print("Updated Japan data")

update()