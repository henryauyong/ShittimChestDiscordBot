import requests
import json

char_data = requests.get("https://api.ennead.cc/buruaka/character?region=japan")
char_data = json.loads(char_data.text)

banner_data = requests.get("https://api.ennead.cc/buruaka/banner?region=japan")
banner_data = json.loads(banner_data.text)

sr = []
ssr = []
limited_ssr = []

rateups = []

# Get SR characters
with open("./gacha_data/japan/sr.txt", "w", encoding="utf-8") as f:
    for i in char_data:
        if i["baseStar"] == 2:
            f.write(i["name"] + "\n")
            sr.append(i["name"])

# Get non-limited SSR characters
for time in banner_data:
    for banner in banner_data[time]:
        if banner["gachaType"] == "LimitedGacha":
            for i in banner["rateups"]:
                if i not in limited_ssr:
                    limited_ssr.append(i)
with open("./gacha_data/japan/ssr.txt", "w", encoding="utf-8") as f:
    for i in char_data:
        if i["baseStar"] == 3 and i["name"] not in limited_ssr:
            f.write(i["name"] + "\n")
            ssr.append(i["name"])

# Get current rateups
for banner in banner_data["current"]:
    banner_rateups = {}
    for rateup_char in banner["rateups"]:
        if rateup_char in sr:
            banner_rateups[rateup_char] = 2
        else:
            banner_rateups[rateup_char] = 3
    rateups.append(banner_rateups)
with open("./gacha_data/japan/rateups.txt", "w", encoding="utf-8") as f:
    json.dump(rateups, f, ensure_ascii=False)