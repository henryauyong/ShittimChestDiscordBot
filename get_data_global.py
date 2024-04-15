import requests
import json

char_data = requests.get("https://api.ennead.cc/buruaka/character")
char_data = json.loads(char_data.text)

banner_data = requests.get("https://api.ennead.cc/buruaka/banner")
banner_data = json.loads(banner_data.text)

sr = []
ssr = []
limited_ssr = []
fes_ssr = []

current_banners = []

# Get SR characters
with open("./gacha_data/global/sr.txt", "w") as f:
    for i in char_data:
        if i["baseStar"] == 2:
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
with open("./gacha_data/global/ssr.txt", "w") as f:
    for i in char_data:
        if i["baseStar"] == 3 and i["name"] not in limited_ssr and i["name"] not in fes_ssr:
            f.write(i["name"] + "\n")
            ssr.append(i["name"])
with open("./gacha_data/global/limited_ssr.txt", "w") as f:
    for i in limited_ssr:
        f.write(i + "\n")
with open("./gacha_data/global/fes_ssr.txt", "w") as f:
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

with open("./gacha_data/global/current_banners.json", "w") as f:
    json.dump(current_banners, f, indent=4)